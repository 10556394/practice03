from django import forms
from . import models
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, PasswordChangeForm,
    PasswordResetForm, SetPasswordForm
)
from django.contrib.auth import (
    authenticate, get_user_model
)
from django.utils.translation import gettext_lazy as _
from .widgets import (
    FileInputWithPreview, FileInputWithoutText, TestWidget, CandidateImagePreview, CandidateImagePreviewTest
)
from django.db.models import Q

UserModel = get_user_model()

class UserForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = (
            'username',
            'email',
            'password',
        )
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'パスワード'})
        }

    password2 = forms.CharField(
        label='確認用パスワード',
        required = True,
        strip = False,
        widget = forms.PasswordInput(attrs={'placeholder': '確認用パスワード'}),
    )

    def clean(self):
        super().clean()
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password != password2:
            raise forms.ValidationError('パスワードと確認用パスワードが一致しません')

    def clean_email(self):
        email = self.cleaned_data['email']
        models.User.objects.filter(email=email, is_active=False).delete()
        return email

class UserAllForm(forms.ModelForm):

    ## departmentをチェックボックスにする書き方１
    departments = forms.ModelMultipleChoiceField(
        queryset = models.Department.objects,
        widget = forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = models.User
        fields = {
            'full_name',
            'departments',
        }
        ## depatrtmentをチェックボックスにする書き方２。これは１と２のどちらでもよい
        #widgets = {
        #    'departments': forms.CheckboxSelectMultiple(choices=()),
        #}


########################################################################
## 自作した、ログインフォームのクラス

class LoginForm(forms.ModelForm):
    class Meta:
        model = models.User

        # MEMO: 括弧を{}から()に変えたら、並び順がその通りに定義された
        # Todo: これって、どっちが正しい書き方なんだろうか？
        fields = (
            'email',
            'password',
        )

        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'パスワード'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        return password


########################################################################
## Djangoを利用した、ログインフォームのクラス

class LoginForm2(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    ## このメッセージを出したいのだが、この処理をするとフォーム2がエラーを出してしまう。
    '''
    def clean(self):
        username = self.cleaned_data.get('username')
        try:
            registed = models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            raise forms.ValidationError('このユーザーは登録されていません')
        else:
            if not registed.is_active:
                raise forms.ValidationError('このユーザーは仮登録状態です')
    '''

########################################################################
## emailでログインできるようにするためのフォームクラス
## AuthenticationFormの内容をコピペし、その一部書き換えて使用する。
class EmailAuthenticationForm(forms.Form):

    email = forms.EmailField(
        label = _('Email'),
        widget = forms.EmailInput(attrs={'autofocus': True,})
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)

        # Set the max length and label for the "username" field.
        self.email_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        self.fields['email'].max_length = self.email_field.max_length or 254
        if self.fields['email'].label is None:
            self.fields['email'].label = capfirst(self.email_field.verbose_name)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        ## この部分の処理が、思った通りに機能していない様子。 ##
        ## 仮登録ユーザーでログインしようとしたりした場合に、メッセージを変えたいのだが…
        try:
            registed = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            raise forms.ValidationError('このユーザーは登録されていません')
        else:
            if not registed.is_active:
                raise forms.ValidationError('このユーザーは仮登録状態です')
            else:
                pass
        #############################################################

        return self.cleaned_data

    def confirm_login_allowed(self, user):

        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return forms.ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'username': _('Email')},
        )



########################################################################
## Djangoを使用した、パスワード変更
class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

########################################################################
## 自作した、リセットパスワードのためのフォームクラス
class ResetPasswordForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = {
            'email'
        }
    def clean_email(self):
        email = self.cleaned_data['email']
        return email



###########################################################################
## Djangoを利用した、パスワードリセットのフォームクラス
class ResetPasswordForm2(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        super().clean()
        email = self.cleaned_data['email']
        try:
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            raise forms.ValidationError('このメールアドレスは登録されていません')
        else:
            pass

        if not user.is_active:
            raise forms.ValidationError('このユーザーは、本登録がされていません。')

class SetPasswordForm2(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


###########################################################################
## Djangoを利用した、記事投稿用のフォームクラス
class ArticleForm(forms.ModelForm):
    class Meta:
        model = models.Article
        fields = (
            'title',
            'body',
        )
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'タイトル 25文字まで'}),
            'body': forms.Textarea(attrs={'placeholder': '本文 500文字まで'}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 25:
            raise forms.ValidationError('25文字を超えています')
        return title


class PhotoForm(forms.ModelForm):
    class Meta:
        model = models.Photo
        fields = ('image',)
        widgets = {
            'image': forms.ClearableFileInput(attrs={'multiple': True}),
        }
        labels = {
            'image': '画像選択',
        }

class PhotoFormAsSelectOne(forms.ModelForm):
    class Meta:
        model = models.Photo
        fields = (
            'image',
            'is_best',
        )
        widgets = {
            'image': forms.ClearableFileInput(),
            #'image': TestWidget(),
            'is_best': forms.CheckboxInput(),
        }
        labels = {
            'image': '画像を選ぶ',
            'is_best': '表紙にする?',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs['class'] = 'image_field_as_article_form2'
        self.fields['is_best'].widget.attrs['class'] = 'photo_choice_is_best'

class PhotoFormForEdit(forms.ModelForm):
    class Meta:
        model = models.Photo
        fields = (
            'image',
            'is_best',
        )
        widgets = {
            'image': FileInputWithoutText(),
            'is_best': forms.CheckboxInput(),
        }
        labels = {
            'image': '画像を選ぶ',
            'is_best': '表紙にする?',
        }

class ImagePreviewForm(forms.ModelForm):
    class Meta:
        model = models.Photo
        fields = ('image', )
        widgets = {
            #'image': FileInputWithPreview(attrs={'multiple': True}),
            'image': FileInputWithPreview(),
        }

###########################################################################
## プロフィール編集用のフォームクラス

ABILITY = (
    (0, 'Level 0'),
    (1, 'Level 1'),
    (2, 'Level 2'),
    (3, 'Level 3'),
    (4, 'Level 4'),
    (5, 'Level 5'),
    (6, 'Level 6'),
    (7, 'Level 7'),
    (8, 'Level 8'),
    (9, 'Level 9'),
    (10, 'Level 10'),
)

class Profile(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = (
            'greeting',
            'partner',
            'ability_power',
            'ability_speed',
            'ability_magic',
            'ability_brain',
            'ability_gard',
            'ability_magicgard',
        )
        widgets = {
            'greeting': forms.Textarea(attrs={'placeholder': '自己紹介：1000文字以内'}),
        }

    ability_power = forms.ChoiceField(widget=forms.Select, choices=ABILITY)
    ability_speed = forms.ChoiceField(widget=forms.Select, choices=ABILITY)
    ability_magic = forms.ChoiceField(widget=forms.Select, choices=ABILITY)
    ability_brain = forms.ChoiceField(widget=forms.Select, choices=ABILITY)
    ability_gard = forms.ChoiceField(widget=forms.Select, choices=ABILITY)
    ability_magicgard = forms.ChoiceField(widget=forms.Select, choices=ABILITY)

    # フォーム作成時、userを受け取る
    def __init__(self, user, *args, **kwargs):
        self.current_user = user
        super(Profile, self).__init__(*args, **kwargs)

        # パートナーとして選ばれているユーザーを取得（ Noneは除外 ）
        partners = models.Profile.objects.values('partner__username').exclude(partner__username=None).all()

        # userのパートナーを取得
        try:
            my_profile = models.Profile.objects.get(user__username = user.username)
        except models.Profile.DoesNotExist:
            my_partner = ''
        else:
            try:
                my_partner = my_profile.partner.username
            except AttributeError:
                my_partner = ''
            else:
                pass

        # パートナーに選ばれているユーザー以外、または自分以外、または Admin以外の user を抽出
        dont_selected_p = models.User.objects.values('username').exclude(
            Q(username__in = partners)|
            Q(username = user.username)|
            Q(is_superuser = True)
        )

        # パートナーに選ばれていないユーザーと自身のパートナーを、フォームの選択肢にセット。
        self.fields['partner'].queryset = models.User.objects.filter(
            Q(username__in = dont_selected_p) |
            Q(username = my_partner)
        )


    # clean_ と Django のバリデーション機能について Memo
    # Modelで設定した validator に準じて、Djangoが自動的にエラーメッセージを作ってくれる
    # なので実質、下記のような clearn_*** の処理は不要。
    # 下記の clean_ability_*** を削除しても、Djangoのバリデーションは正常に機能するが、せっかく作ったので残しておく。

    def clean_ability_power(self):
        a = self.cleaned_data['ability_power']
        a = int(a)
        if a < 0 or 10 < a:
            raise forms.ValidationError('0～10で選んでください')
        return a

    def clean_ability_speed(self):
        b = self.cleaned_data['ability_speed']
        b = int(b)
        if b < 0 or 10 < b:
            raise forms.ValidationError('0～10で選んでください')
        return b

    def clean_ability_magic(self):
        c = self.cleaned_data['ability_magic']
        c = int(c)
        if c < 0 or 10 < c:
            raise forms.ValidationError('0～10で選んでください')
        return c

    def clean_ability_brain(self):
        d = self.cleaned_data['ability_brain']
        d = int(d)
        if d < 0 or 10 < d:
            raise forms.ValidationError('0～10で選んでください')
        return d

    def clean_ability_gard(self):
        e = self.cleaned_data['ability_gard']
        e = int(e)
        if e < 0 or 10 < e:
            raise forms.ValidationError('0～10で選んでください')
        return e

    def clean_ability_magicgard(self):
        f = self.cleaned_data['ability_magicgard']
        f = int(f)
        if f < 0 or 10 < f:
            raise forms.ValidationError('0～10で選んでください')
        return f


class ProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ('image',)
        widgets = {
            'image': FileInputWithPreview(),
        }
        labels = {
            'image': 'プロフィール画像を選択する',
        }

class CommentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body'].widget.attrs['id'] = 'comment_section_written_by_user'

    class Meta:
        model = models.Comment
        fields = ('body', )
        labels = {
            'body': 'コメント',
        }
        widgets = {
            'body': forms.TextInput(attrs={'placeholder': 'コメントを入力 25文字まで'}),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = models.Reply
        fields = ('body', )
        labels = {
            'body': '返信',
        }
        widgets = {
            'body': forms.TextInput(attrs={'placeholder': '返信コメントを入力 25文字まで'}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = models.Tag
        fields = ('tag', )
        labels = {
            'tag': 'タグ',
        }
        widgets = {
            'tag': forms.TextInput(attrs={'placeholder': 'タグを追加 30文字まで'}),
        }


class TagDetailForm(forms.ModelForm):

    def __init__(self, tag=None, *args, **kwargs):
        self.current_tag = tag
        super(TagDetailForm, self).__init__(*args, **kwargs)

        images = models.Photo.objects.filter(article__tagged_art__tag=tag)
        self.fields['image'].queryset = images

    class Meta:
        model = models.TagDetail
        fields = (
            'image',
            'detail'
        )
        widgets = {
            # 下記は、テストにて模索したテストファイル。記録のため保存。
            #'image': CandidateImagePreviewTest(),
            'image': CandidateImagePreview(),
            'detail': forms.Textarea(attrs={'placeholder': '説明文を入力 500文字まで'})
        }