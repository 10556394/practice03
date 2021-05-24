from django.conf import settings
from django.shortcuts import render, redirect
from . import forms
from .models import User, Article, Photo, Profile, Department, Comment, Reply, Bookmark, Album, Tag, Follow, Good, Visit, TagDetail
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.template.loader import render_to_string
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.views import generic
from django.core import mail
from django.contrib.auth import views
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, LoginView, LogoutView
from django.forms import modelformset_factory
from django.http.response import JsonResponse
import json
from django.utils import timezone
from datetime import datetime as dt
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

# 非同期通信設定 ON(True)/OFF(False)
is_XHR = True

# 記事投稿画面：登録可能な最大数
article_photo_form_cnt = 10

# NoImageへのパス
URL_NO_IMAGE_FACE = '/static/users/images/no_image_face.png'

# 日付を文字列に変換する
def get_str_date_now():
    now_date = dt.now()
    str_date = now_date.strftime('%Y年%m月%d日 %H:%M')
    str_date_without0 = str_date.replace('年0', '年').replace('月0', '月')
    return str_date_without0

# 初回訪問かどうかを調べる
def check_is_first_visit(request):
    try:
        request.session['username']
    except KeyError:
        return True
    else:
        return False

# おススメ順で記事を取得する
def getting_articles_in_order_of_recommendation(request):
    username = request.session['username']

    # Userがアクセスしたことのあるタグ
    visits = Visit.objects.filter(user__username=username).values('article__tagged_art__tag').distinct()
    tags = []
    for visit in visits:
        tags.append(visit['article__tagged_art__tag'])

    # そのタグのアクセス総数
    pvs = []
    for tag in tags:
        pvs.append(Visit.objects.filter(article__tagged_art__tag=tag, user__username=username).count())

    # タグをアクセス順に並べる（タグ Noneは常に未訪問状態と同等に扱う）
    tag_dict = dict(zip(tags, pvs))
    tag_dict = sorted(tag_dict.items(), key = lambda x:x[1], reverse=True)
    tags = []
    for tag in tag_dict:
        if tag[0] == None:
            pass
        else:
            tags.append(tag[0])

    # アクセスしたことのないタグも追加
    e_tags_dict = Tag.objects.exclude(tag__in=tags).values('tag').distinct()
    e_tags = []
    for e_tag in e_tags_dict:
        e_tags.append(e_tag['tag'])

    tag_all = tags + e_tags

    # アクセスの多いタグ順に記事取得
    art_objs = []
    for t in tag_all:
        art_objs.append(Article.objects.filter(tagged_art__tag=t).order_by('-pk'))
    art_objs.append(Article.objects.filter(tagged_art__tag__isnull=True).order_by('-pk'))

    # 重複記事を削除
    art_all = []
    for art_queryset in art_objs:
        for art in art_queryset:
            art_all.append(art)
    art_all = sorted(set(art_all), key=art_all.index)

    return art_all

# Create your views here.

def todo_show(request):
    return render(request, 'users/todo.html')

def show_all_user(request):
    users = User.objects.filter(is_superuser=False)
    context = {
        'users': users,
        'title': 'すべてのユーザー',
    }
    return render(request, 'users/show_all_user.html', context)

def show_follow_user(request):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        pass

    # 自身がフォローしているユーザーを取得
    f_queryset = Follow.objects.filter(user__username=username)
    follow_users = []
    for f in f_queryset:
        follow_users.append(User.objects.get(username=f.followed_user.username))

    # 自信をフォローしているユーザーを取得
    f_queryset2 = Follow.objects.filter(followed_user__username=username)
    follow_users2 = []
    for f2 in f_queryset2:
        follow_users2.append(User.objects.get(username=f2.user.username))

    context = {
        'users': follow_users,
        'followers': follow_users2,
        'title1': 'あなたがフォローしているユーザー',
        'title2': 'あなたをフォローしているユーザー',
    }
    return render(request, 'users/show_follow_user.html', context)

def index(request):
    my_message = ''
    dj_message = ''

    is_first_visit = check_is_first_visit(request)

    if request.user :
        try :
            regist_user = User.objects.get(username=request.user.username)
        except User.DoesNotExist:
            dj_message = ''
        else:
            if is_first_visit:
                dj_message =  'ようこそ、{}さん。'.format(request.user.username)
            else:
                dj_message = ''

            request.session['username'] = regist_user.username
            try:
                profile = Profile.objects.get(user=regist_user)
            except Profile.DoesNotExist:
                pass
            else:
                request.session['userimage'] = profile.image.url

            #articles = Article.objects.order_by('-pk').all()
            articles = getting_articles_in_order_of_recommendation(request)
            bookmarks = Bookmark.objects.filter(user=request.user)
            # is_bestのついた写真を選択。それが存在しない場合は、登録画像１枚目を選択。
            arts = articles
            photos = []
            for art in arts:
                is_best = False
                art_photos = Photo.objects.filter(article__id=art.id)
                for art_photo in art_photos:
                    if art_photo.is_best:
                        is_best = True
                if is_best:
                    photos.append(Photo.objects.filter(article__id=art.id, is_best=True).first())
                else:
                    photos.append(Photo.objects.filter(article__id=art.id).first())

            # タグを人気順（タグづけされている記事の PV合計が多い順）で取得
            t_cnts = []
            t_list = []
            tag_all = Tag.objects.values_list('tag', flat=True).all().distinct()

            for tag in tag_all:
                t_cnts.append(Visit.objects.filter(article__tagged_art__tag=tag).count())
            visit_and_tags = dict(zip(t_cnts, tag_all))
            sorted_tags = sorted(visit_and_tags.items(), reverse=True)

            for sorted_tag in sorted_tags:
                t_list.append(sorted_tag[1])
            pop_tags = t_list

            contents = {
                'photos': photos,
                'articles': articles,
                'message': dj_message,
                'bookmarks': bookmarks,
                'is_XHR': is_XHR,
                'pop_tags': pop_tags,
            }

            return render(request, 'users/articles/index.html', contents)
    else:
        dj_message = ''

    if 'username' in request.session:
        my_message = request.session['username'] + 'でログインしています（自作Login 成功）'
    else:
        my_message = ''

    photos = Photo.objects.all().order_by('?')[0:100]
    context = {
        'photos': photos,
        'my_message': my_message,
        'dj_message': dj_message
    }
    return render(request, 'users/index.html', context)

def user_form(request):
    if request.method == 'POST':
        user = forms.UserForm(request.POST)
        try:
            username = User.objects.filter(username=request.POST['username']).values()[0]['username']
        except IndexError:
            pass
        else:
            initial_dict = {
                'username': request.POST['username'],
                'email': request.POST['email'],
            }
            form = forms.UserForm(initial=initial_dict)
            context = {
                'forms': form,
                'message': 'ユーザー名：'+ username + 'は、すでに登録されています。別の名前を登録してください。'
            }
            return render(request, 'users/user_form.html', context)

        try:
            email = User.objects.filter(email=request.POST['email']).values()[0]['email']
        except IndexError:
            pass
        else:
            message = 'メールアドレス[' + email + ']はすでに登録されています'
            context = {
                'message': message,
                'forms': user,
            }
            return render(request, 'users/user_form.html', context )

        if user.is_valid():
            user_model = user.save(commit=False)
            #追加で項目を登録するならここに書く
            user_model.password = make_password(user_model.password)
            user_model.is_active = False
            user_model.save()

            current_site = get_current_site(request)
            domain = current_site.domain

            message = '本登録のメールを送信しました。\nメールの確認URLをクリックし、本登録を完了させてください'
            context = {
                'message': message,
                'domain': domain,
                'token': dumps(user_model.username),
                'user': user_model,
            }
            subject = user_model.username + 'さんへ。本会員登録のご案内。'
            mail_body = render_to_string('users/mail_templates/body.txt', context)
            user_model.email_user(subject, mail_body)
            return render(request, 'users/message.html', context)
        else:
            # パスワードと確認用パスワードが異なっていた場合の処理
            form = forms.UserForm(request.POST)
            context = {
                'forms': form,
            }
            return render(request, 'users/user_form.html', context)

    if request.method == 'GET':
        form = forms.UserForm()
        context = {
            'forms': form
        }
        return render(request, 'users/user_form.html', context)

def main_regist(request, token):
    time_out_seconds = getattr(settings, 'ACTiVATON_TIMEOUT_SECONDS', 60*60*24)
    try:
        token_loaded = loads(token, max_age=time_out_seconds)
    #期限切れ
    except SignatureExpired:
        message = '本登録URLの有効期限が切れています。'
        context = {
            'message': message
        }
        return render(request, 'users/message.html', context)
    # tokenが違っている
    except BadSignature:
        message = '不正なトークンです。URLをご確認ください'
        context = {
            'message': message
        }
        return render(request, 'users/message.html', context)
    # token問題なし
    else:
        try:
            user = User.objects.get(username=token_loaded)
        except User.DoseNotExist:
            message = 'このユーザー名は存在していません'
            context = {
                'message': message
            }
            return render(request, 'users/message.html', context)
        else:
            if not user.is_active:
                user.is_active = True
                user.save()
                context = {
                    'message' : token_loaded + 'の本登録を行いました。\n続けて、職群と氏名を登録してください。',
                    'user': user
                }
                return render(request, 'users/regist_complete.html', context)
            else:
                context = {
                    'message': token_loaded + 'は、すでに会員登録が完了しています',
                }
                return render(request, 'users/message.html', context)

def regist_user_info(request, uuid=None):
    if request.method == 'POST':
        if uuid:
            user = get_object_or_404(User, uuid=uuid)
        else:
            user = User()
        user_form = forms.UserAllForm(request.POST, instance=user)
        if user_form.is_valid():
            ## !! ManytoManyFieldをsaveする場合、commit=Falseを使うとうまく動作しない !!
            #user_regist = user_form.save(commit=False)
            user_form.save()
            message = 'ユーザー情報を追加しました。'
        else:
            context = {
                'forms': user_form,
                'message': '入力が正しく行われていません。選択内容をご確認ください。'
            }
            return render(request, 'users/regist_user_info.html', context)
        context = {
            'message': message,
        }
        return render(request, 'users/message.html', context)

    else:
        user_form = forms.UserAllForm()
        user = User.objects.get(uuid=uuid)
        context = {
            'user': user,
            'forms': user_form,
        }
        return render(request, 'users/regist_user_info.html', context)

def user_list(request):
    users = User.objects.all()
    context = {
        'users': users
    }
    return render(request, 'users/user_list.html', context)

def sample_funciton():
    #########################################################################################
    ## ブロック化するため、インデントをしている。実際に使用するときはインデントを解除すること
    ## この処理だと、 login.errors = User with this Email address already exists. となる
    ## すでにメールアドレスが存在しているため、is_validがFalseになってしまうらしい。
    ## ToDo:is_validを使わず?に、入力情報をバリデーションして、ログイン処理を完成させたい。
    """
    def login(request, email=None):
        if request.method == 'POST':
            login = forms.LoginForm(request.POST)
            if login.is_valid():
                registed = get_object_or_404(User, email=request.POST['email'])
                registed_pass = registed.password
                if check_password(request.POST['password'], registed_pass):
                    username = registed.username
                    message = 'ようこそ' + username + 'さん'
                else:
                    message = 'ログイン情報が違いました'
            else:
                message = login.errors
            context = {
                'message': message
            }
            return render(request, 'users/message.html', context)

        else:
            login_form = forms.LoginForm()
            context = {
                'forms': login_form,
            }
            return render(request, 'users/login.html' , context)
    """

def login(request, email=None):
    # メッセージを初期化
    message = ''

    if request.method == 'POST':
        login = forms.LoginForm(request.POST)
        try:
            registed = User.objects.get(email=request.POST['email'])
        except User.DoesNotExist:
            message = 'このメールアドレスは登録されていません'
            context = {
                'message': message,
                'forms': login,
            }
            return render(request, 'users/login.html', context)
        else:
            registed_pass = registed.password

        if not registed.is_active:
            message = 'このユーザーは仮登録状態です。'
            context = {
                'message': message,
                'forms': login,
            }
            return render(request, 'users/login.html', context)

        ## Login成功した時の処理。SESSIONの処理もここからスタート
        if check_password(request.POST['password'], registed_pass):
            request.session['username'] = registed.username
            request.session['email'] = registed.email
            context = {
                'user': registed
            }
            return render(request, 'users/show.html', context)

        else:
            message = 'パスワード、またはメールアドレスが違います'
            context = {
                'message': message,
                'forms': login,
            }
            return render(request, 'users/login.html', context)

    else:
        login_form = forms.LoginForm()
        context = {
            'forms': login_form,
        }
        return render(request, 'users/login.html' , context)

def logout(request):
    request.session.clear()
    context = {
        'message': 'ログアウトしました。'
    }
    return render(request, 'users/message.html', context)

class Login2(LoginView):
    # またもエラーにはまったので、メモ　2021.3.22
    # 今回のエラー：TypeError at /users/login2　__init__() takes 1 positional argument but 2 were given
    # 原因：uals.py がpath('login2', views.Login2, name='login2'),ってなってた、
    # 正しくは path('login2', views.Login2.as_view(), name='login2'),

    form_class = forms.LoginForm2
    template_name = 'users/login2.html'

class Logout2(LoginRequiredMixin, LogoutView):
    template_name = 'users/login2.html'

class Login3(LoginView):
    form_class = forms.EmailAuthenticationForm
    template_name = 'users/login3.html'

def reset_password(request):
    ######################################################################
    ## 自作したパスワードリセット。まだ、制作途中
    ## Djangoにもパスワードリセットの機能があるとのことで、そっちに切り替えることにした。
    message = ''

    if request.method == 'POST':
        email = request.POST['email']
        try:
            reset_pass_user = User.objects.get(email=email)
        except User.DoesNotExist:
            message = 'このメールアドレスは、登録されていません。'
            obj = forms.ResetPasswordForm(request.POST)
            context = {
                'forms': obj,
                'message': message,
            }
            return render(request, 'users/reset_password.html', context)
        else:
            ## ここからが作成途中。
            ## 現時点ではメールを送信せず、メッセージを表示している。
            context = {
                'message': email + '\nにメールを送信しました。'
            }
            return render(request, 'users/message.html', context)

    else:
        obj = forms.ResetPasswordForm()
        context = {
            'forms': obj
        }
        return render(request, 'users/reset_password.html', context)

class ResetPassword(views.PasswordResetView):

        # パスワードリセットのリクエストにて、エラーが発生。
        # なぜか、palutena@gmail.com で送信するとTypeError　getattr(): attribute name must be string と出る
        # でも、rrr@gmail.comだと成功する。
        # どうも、登録されているメールアドレスに送信するとこのエラーになるようだ。

        ################## ここから、再び試行錯誤が続く。記録として行動のメモを取っておく 2021.3.18 　############################
        # ためしに、models.pyのUser.emailの。unique=Trueを削除してみたけれど、ダメだった。unique=Falseにしてもダメだった。
        # form_class = forms.ResetPasswordForm2 をコメントアウトしても、何も変わらない。
        # エラーが出るときは、　http://127.0.0.1:8000/users/reset_password2/
        # エラーが出ないときは、http://127.0.0.1:8000/users/reset_password2/done/

        # 解決！
        # model.pyにあるEMAIL_FIELD = 'email',の、カンマを削除したら、解決した！
        # 解決までの記録：エラーメッセージをたどって解決した。
        # getattrを調べたところ、今回のエラーは getattr(u, email_field_name) のemail_field_nameが文字列になっていないことが原因と判明
        # じゃ、そのemail_field_nameはどこから来ているのかを調べた。
        # email_field_nameは、email_field_name = UserModel.get_email_field_name()　って記述があった。
        # つまり、UserModelの時点で、何かがおかしいと判断できる。
        # そして、PasswordResetFormの中身を調べたりした。
        # そうしたら、EMAIL_FIELD = 'email',を発見。あれ、カンマ（,）っておかしくないか？と仮説がたつ。
        # 試してみたところ、解決した！
        # 今回のエラー解決のロジックは、今後も非常に大切になる。
        # このエラーを自力解決できたのは、すごいと思う。エラー解決スキルも、確実に身についている。

    subject_template_name = 'users/mail_templates/reset_password/subject.txt'
    email_template_name = 'users/mail_templates/reset_password/message.txt'
    template_name = 'users/reset_password2.html'
    form_class = forms.ResetPasswordForm2
    success_url = reverse_lazy('users:reset_password2_done')

class ResetPasswordDone(views.PasswordResetDoneView):
    template_name = 'users/reset_password2_done.html'

class ResetPasswordConfirm(views.PasswordResetConfirmView):
        # AssertionErrorという、見慣れないエラーが発生したのでメモ。
        # 原因：assert 'uidb64' in kwargs and 'token' in kwargs
        #      なんだか、キーワードに uidb64ってのが入っていないからエラーになっているらしい
        # 解決法：url.pyにて、値の受け取り変数を下記のようにしたら解決した。
        #         path('reset_password2/confirm/<str:uidb64><str:token>/...
        #         しかし、これはうまく次につなげられるのか？
        #         ちなみに、この時の再設定用URLは、{{ protocol }}://{{ domain }}{% url 'users:reset_password2_confirm' uuid token %}

            # 新たな問題が発生
            # 内容：再設定用フォームに、入力フォームが表示されない。
            # 　　　おそらく、ユーザーの受け取りがうまくいっていないと思われる。
            # 解決法：1.再設定URLを下記の通り変更
            # 　　　　　前）{% url 'users:reset_password2_confirm' uuid token %}
            # 　　　　　後）{% url 'users:reset_password2_confirm' uid token %}
            #　　　　 2.受け取りURLの記述を下記に変更
            #　　　　　前）reset_password2/confirm/<str:uidb64><str:token>/
            # 　　　 　後）reset_password2/confirm/<str:uidb64>/<str:token>/

    form_class = forms.SetPasswordForm2
    template_name = 'users/reset_password2_confirm.html'
    success_url = reverse_lazy('users:reset_password2_complete')

class ResetPasswordComplete(views.PasswordResetCompleteView):
    template_name = 'users/reset_password2_complete.html'

class ChangePassword(PasswordChangeView):
    # 問題発生：ここに来ようとしても、http://127.0.0.1:8000/accounts/login/?next=/users/change_password/に飛んでしまい、エラーになる
    # setting.py に、LOGIN_URL='users:login'と記述したら、とび先が、http://127.0.0.1:8000/users/login?next=/users/change_password/に変わった。
    # おそらくだが、今回DjangoViewを使ってパスワード変更を作成した。が、この場合LoginもDjangoの機能を使って作成しないと、
    # Loginしているって認識されていないのかもしれない。
    # ToDo: やっぱり、Login機能をDjangoにて作成し、この仮説を立証する必要がある 2021.3.21
    # 仮説立証：やはりDjango機能にてLoginした場合、ちゃんとパスワード変更画面が表示された！ 2021.3.22
    # でも不思議なことに、一度DjangoLoginでログインした後に、自作Loginでログインしたら、今度はちゃんと動作した
    form_class = forms.ChangePasswordForm
    success_url = reverse_lazy('users:change_password_complete')
    template_name = 'users/change_password.html'

class ChangePasswordComplete(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'users/change_password_complete.html'

class ListViewTest(generic.ListView):
    users = User
    template_name = 'users/list_view_test.html'
    def get_queryset(self):
        return User.objects.all()

class DetailViewTest(generic.DetailView):
    model = User
    template_name = 'users/detail_view_test.html'

def my_page(request):
    try:
        username = request.session['username']
    except KeyError:
        return redirect('users:index')
    else:
        pass

    # 記事
    articles = Article.objects.filter(user__username=username).order_by('-pk')
    followers = Follow.objects.values('followed_user__username').filter(user__username=username)
    followers_article = Article.objects.filter(user__username__in=followers).last()

    # アクセス情報
    pv = Visit.objects.filter(article__user__username=username).count()
    good_cnt = Good.objects.filter(article__user__username=username).count()
    bm_cnt = Bookmark.objects.filter(article__user__username=username).count()
    comment_cnt = Comment.objects.filter(article__user__username=username).count()

    # プロフィール
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        profile = ''
    else:
        pass

    context = {
        'username': username,
        'articles': articles,
        'followers_article': followers_article,
        'pv': pv,
        'good_cnt': good_cnt,
        'bm_cnt': bm_cnt,
        'comment_cnt': comment_cnt,
        'profile': profile,
    }
    return render(request, 'users/articles/my_page.html', context)


# 動作に不具合が見つかった。 画像選択ウィンドウを複数回立ち上げて画像登録しようとすると、最後に選択した画像しか登録されない そのため、この機能は使わない
def article_form(request):
    a_form = forms.ArticleForm
    p_form = forms.PhotoForm
    t_form = forms.ImagePreviewForm

    contents = {
        'forms': a_form,
        'photos': p_form,
        'imgs': t_form,
    }
    return render(request, 'users/articles/article_form.html', contents)

# 記事登録は、こっちに以降した
def article_form2(request):
    a_form = forms.ArticleForm
    PhotoFormSet = modelformset_factory(
        model = Photo,
        form = forms.PhotoFormAsSelectOne,
        extra = article_photo_form_cnt,
    )
    p_forms = PhotoFormSet(queryset=Photo.objects.none())
    context = {
        'forms': a_form,
        'photo_forms': p_forms,
    }
    return render(request, 'users/articles/article_form2.html', context)

# 動作に不具合が見つかった。画像選択ウィンドウを複数回立ち上げて画像登録しようとすると、最後に選択した画像しか登録されない そのため、この機能は使わない
def article_regist(request):
    if request.method == 'POST':
        article = forms.ArticleForm(request.POST)
        #images = forms.PhotoForm(request.POST, request.FILES)
        images = forms.ImagePreviewForm(request.POST, request.FILES)

        if request.session['username']:
            username = request.session['username']
        else:
            message = '記事を投稿するには、ログインしてください。'
            return render(request, 'users/message.html', context)

        if article.is_valid() and images.is_valid():
            article_model = article.save(commit=False)
            article_model.user = User.objects.get(username=username)
            article_model.save()
            article_id = Article.objects.order_by('-pk')[:1].values()[0]['id']
            images = request.FILES.getlist('image', False)
            for image in images:
                image_instance = Photo(
                    image = image,
                    article = Article.objects.get(pk=article_id),
                )
                image_instance.save()
            message = '投稿が完了しました。'
        else:
            message = '登録に失敗しました。'
    else:
        message = '正しいアクセスではありません。'

    context = {
        'message': message,
    }
    return render(request, 'users/message.html', context)

# 画像登録は、こっちに以降した
def article_regist2(request):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインが必要です'}
        return render(request, 'users/message.html', context)
    else:
        pass

    if request.method == 'POST':
        article = forms.ArticleForm(request.POST)
        PhotoFormSet = modelformset_factory(
            model = Photo,
            form = forms.PhotoForm,
            extra = article_photo_form_cnt,
        )
        photos = PhotoFormSet(request.POST, request.FILES)
        tags = request.POST.getlist('tags[]')

        if article.is_valid() and photos.is_valid():
            article_model = article.save(commit=False)
            article_model.user = User.objects.get(username=username)
            article_model.save()
            article_last = Article.objects.order_by('id').last()

            photos_t = photos.save(commit=False)
            for i, photo in enumerate(photos_t):
                photo.article = article_last
                for n in range(article_photo_form_cnt):
                    if request.FILES.get('form-{}-image'.format(n))  == photo.image :
                        if request.POST.get('form-{}-is_best'.format(n)) == 'on':
                            photo.is_best = True
                        else:
                            photo.is_best = False
                photo.save()

            for tag in tags:
                tag_model = Tag(
                    user =  User.objects.get(username=username),
                    tag = tag
                )
                tag_model.save()
                # またも引っかかったので Memo。m2mを登録する際は、対象の id を.addするらしい。
                # ほかのデータと同じようには、登録ができないようだ。
                tag_model.article.add(article_last.id)

            request.session['message'] = '記事を投稿しました'
            return redirect('users:article_show', article_last.id )

        else:
            context = {
                'forms': article,
                'photo_forms': photos,
                'message': '投稿に失敗しました。入力内容をご確認ください。'
            }
            return render(request, 'users/articles/article_form2.html', context)
    else:
        context = {'message': 'アクセスが不正です'}

    return render(request, 'users/message.html', context)


def show_my_article_list(request):
    try:
        user = User.objects.get(username=request.session['username'])
    except KeyError:
        context = {
            'message': 'このページへアクセスするには、ログインが必要です。'
        }
        return render(request, 'users/message.html', context)
    else:
        pass

    try:
        message = request.session['message']
    except:
        message = ''
    else:
        del request.session['message']

    articles = Article.objects.filter(user=user).order_by('-pk')

    if articles:
        context = {
            'message': message,
            'username': request.session['username'],
            'articles': articles,
        }
        return render(request, 'users/articles/article_list.html', context)
    else:
        context = {
            'message': message,
            'username': request.session['username']
        }
        return render(request, 'users/articles/no_article.html', context)

def article_show(request, id):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        pass

    try:
        message = request.session['message']
    except KeyError:
        message = ''
    else:
        del request.session['message']

    article = Article.objects.get(pk=id)
    photos = Photo.objects.filter(article=article)
    author = User.objects.get(username=article.user.username)
    comments = Comment.objects.filter(article=article).order_by('-posted_date')
    replys = Reply.objects.filter(comment__in=comments).order_by('-posted_date')
    albums = Album.objects.filter(user__username=username)
    tags = Tag.objects.filter(article=article).order_by('-tagged_date')
    bookmark = Bookmark.objects.filter(user__username=username, article__id=id)
    good = Good.objects.filter(user__username=username, article__id=id)
    good_cnt = Good.objects.filter(article__id=id).count()

    # 関連記事取得
    # タグ以外にも、タイトルのLike検索でも関連記事をひっかける
    # 追加：同じ作者の記事もひっかける。そのパートナーの記事もひっかける。
    tag_titles = tags.values('tag')
    art_title = article.title
    art_username = article.user.username

    try :
        partner_name = article.user.person.partner.username
    except ObjectDoesNotExist:
        partner_name = ''
    except AttributeError:
        partner_name = ''
    else:
        pass

    related_articles = Article.objects.filter(
        Q(tagged_art__tag__in=tag_titles) |
        Q(title__icontains=art_title) |
        Q(user__username=art_username) |
        Q(user__username=partner_name)
    ).distinct()
    related_articles = related_articles.exclude(id=id).order_by('-pk')
    # Memo：↓ランダム順にすると、うまく重複削除できなくなるみたい
    # related_articles = related_articles.order_by('?')

    try:
        author_profile = Profile.objects.get(user=author)
    except Profile.DoesNotExist:
        author_profile = ''

    form = forms.CommentForm
    reply_form = forms.ReplyForm
    tag_form = forms.TagForm

    context = {
        'username': username,
        'article': article,
        'photos': photos,
        'author': author,
        'author_profile': author_profile,
        'forms': form,
        'reply_forms': reply_form,
        'tag_forms': tag_form,
        'comments': comments,
        'replys': replys,
        'albums': albums,
        'is_XHR': is_XHR,
        'tags': tags,
        'bookmark': bookmark,
        'good': good,
        'good_cnt': good_cnt,
        'related_articles': related_articles,
        'message': message,
    }
    return render(request, 'users/articles/article_show.html', context)

def article_edit(request, id=None):
    if id:
        article = Article.objects.get(id=id)
        photos = Photo.objects.filter(article=article)
    else:
        context = {
            'message': '編集する記事が選択されていません'
        }
        return render(request, 'users/message.html', context)

    try:
        username = request.session['username']
    except KeyError:
        context = {
            'message': '記事を編集するにはログインしてください。'
        }
        return render(request, 'users/message.html', context)
    else:
        initial_dict = {
            'title': article.title,
            'body': article.body,
        }
        article_form = forms.ArticleForm(initial=initial_dict)
        can_regist_photo_cnt = article_photo_form_cnt - photos.count()
        PhotoFormSet = modelformset_factory(
            model = Photo,
            form = forms.PhotoFormForEdit,
            extra = can_regist_photo_cnt,
            can_delete = True,
        )
        photo_forms = PhotoFormSet(queryset=photos)
        context = {
            'username': username,
            'forms': article_form,
            'id': article.id,
            'photo_forms': photo_forms,
        }
        return render(request, 'users/articles/article_edit.html', context)

def article_edit_run(request, id=None):
    if request.method == 'POST':
        article = Article.objects.get(pk=id)
        form = forms.ArticleForm(request.POST, instance=article)
        PhotoFormSet = modelformset_factory(
            model = Photo,
            form = forms.PhotoForm,
            extra = article_photo_form_cnt,
            can_delete = True,
        )
        photos = PhotoFormSet(request.POST, request.FILES)
        photo_cnt_already_exists = Photo.objects.filter(article=article).count()

        # MEMO:エラー ['マネジメントフォームのデータが見つからないか、改竄されています。'] が出た場合
        # 解決法１：templateファイルに、{{ photo_forms.management_form }} が、記述されているかを確認。なければ追記。
        if form.is_valid() and photos.is_valid():
            form.save()
            photos_t = photos.save(commit=False)
            start_point = 0

            # 新規登録の画像も処理するので、この形。
            for i, photo in enumerate(photos_t):
                photo.article = article
                photo.save()

            # is_best を登録＆修正：QuerySetでphotoを取得しなおして、is_bestを設定。
            photos_e = Photo.objects.filter(article=article)
            for i, photo in enumerate(photos_e):
                if i < photo_cnt_already_exists:
                    is_normal_proc = True
                else:
                    is_normal_proc = False

                # 編集以前より登録されていた画像の is_best 修正（ 順番通りフォームに並ぶので、普通に処理 ）
                if is_normal_proc:
                    if request.POST.get('form-{}-is_best'.format(i)) == 'on':
                        photo.is_best = True
                    else:
                        photo.is_best = False

                # 今回の編集で、新規に登録された画像の is_best 登録（１つ飛ばしなど、フォームへの変則的入力を想定 ）
                # log：こういう複雑な処理を書くときは、紙に図説してアタマを整理するといい。本当に、痛感した。
                else:
                    for n in range(start_point, article_photo_form_cnt):
                        if request.FILES.get('form-{}-image'.format(n)):
                            if request.POST.get('form-{}-is_best'.format(n)) == 'on':
                                photo.is_best = True
                            else:
                                photo.is_best = False
                            start_point = n + 1
                            break

                photo.save()

            # Todo：削除ボタンを押した画像が消えない。処理を追記する。
            # このやり方は、おそらくスマートなやり方ではないと思うけれど、とりあえず動いたのでよしとする。
            roop_count = Photo.objects.filter(article=article).count()
            for i in range(roop_count):
                if request.POST.get('form-{}-DELETE'.format(i)) == 'on':
                    del_photo_id = request.POST.get('form-{}-id'.format(i))
                    Photo.objects.filter(pk=del_photo_id).delete()

            request.session['message'] = '記事を編集しました。'
            return redirect('users:article_show', id)
        else:
            context = {
                '編集に失敗しました。'
            }
        return render(request, 'users/message.html', context)

def article_delete(request, id=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {
            'message': '記事を削除するにはログインが必要です。',
        }
        return render(request, 'users/message.html', context)
    else:
        pass

    if id:
        Article.objects.get(pk=id).delete()
        request.session['message'] = '記事を削除しました。'
        return redirect('users:show_my_article_list')
    else:
        context = {
            'message': '削除する記事が指定されていません。'
        }

    return render(request, 'users/message.html', context)

def profile_form(request):
    if request.session['username']:
        username = request.session['username']
        user = User.objects.get(username=username)
        try:
            user_p = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            initial_dict = {}
            initial_img = {}
        else:
            initial_dict = {
                'greeting': user_p.greeting,
                'partner': user_p.partner,
                'ability_power': user_p.ability_power,
                'ability_speed': user_p.ability_speed,
                'ability_brain': user_p.ability_brain,
                'ability_gard': user_p.ability_gard,
                'ability_magic': user_p.ability_magic,
                'ability_magicgard': user_p.ability_magicgard,
            }
            initial_img = {
                'image': user_p.image,
            }
        # user情報をformへ送る
        form = forms.Profile(user=user, initial=initial_dict)
        photo = forms.ProfilePhotoForm(initial=initial_img)

        try:
            message = request.session['message']
        except KeyError:
            message = ''
        else:
            del request.session['message']

        context = {
            'username': username,
            'forms': form,
            'photo': photo,
            'message': message,
        }

        return render(request, 'users/articles/profile_form.html', context)
    else:
        context = {
            'message': 'プロフィール登録をするには、ログインしてください。',
        }
        return render(request, 'user/message.html', context)

def profile_regist(request):

    if request.method == 'POST':
        username = request.session['username']
        user = User.objects.get(username=username)
        try:
            profile = Profile.objects.get(user=user)

        # 新規登録の場合
        except Profile.DoesNotExist:
            # user情報をformへ送る
            profile = forms.Profile(user=user, data=request.POST)
            if request.FILES:
                photo = forms.ProfilePhotoForm(request.POST, request.FILES)
                is_photo_save = True
            else:
                is_photo_save = False

            if profile.is_valid():
                profile_model = profile.save(commit=False)
                profile_model.user = User.objects.get(username=username)
                if is_photo_save:
                    profile_model.image = request.FILES['image']
                profile_model.save()
                request.session['message'] = 'プロフィールを登録しました。'
                p = Profile.objects.get(user=user)
                request.session['userimage'] = p.image.url
                return redirect('users:profile_show', username)
            else:
                # initial_dictで一つ一つ入れなくても、request.POSTで一括取得できるみたい。
                #initial_dict = {
                #    'greeting': request.POST['greeting'],
                #    'partner': request.POST['partner'],
                #    'ability_power': request.POST['ability_power'],
                #    'ability_speed': request.POST['ability_speed'],
                #    'ability_magic': request.POST['ability_magic'],
                #    'ability_brain': request.POST['ability_brain'],
                #    'ability_gard': request.POST['ability_gard'],
                #    'ability_magicgard': request.POST['ability_magicgard'],
                #}
                #form = forms.Profile(initial=initial_dict)

                # request.POSTもいいけれど、そもそも profile でフォームデータを受け取っているから、profileが入力情報つきのフォームオブジェクトになってた
                #profile = forms.Profile(request.POST)

                # forms.ValidationError のエラーメッセージは、この形で受け取れるようだ。
                # しかし、こうしなくても、テンプレート側にて、formname.error を記述すれば、フォームごとのエラーメッセージを受け取れる
                error_msg = profile.errors

                message = 'プロフィール登録に失敗しました。入力情報を確認してください'

            context = {
                'message': message,
                'forms': profile,
                'username': username,
                'photo': photo,
                'error_msg': error_msg,
            }
            return render(request, 'users/articles/profile_form.html', context)

        # 編集の場合
        else:
            # user情報をformへ送る
            form = forms.Profile(user=user, data=request.POST, instance=profile)
            if request.FILES:
                photo = forms.ProfilePhotoForm(request.POST, request.FILES, instance=profile)
                is_photo_save = True
            else:
                is_photo_save = False

            if form.is_valid():
                form.save()
                if is_photo_save:
                    photo.save()
                request.session['message'] = 'プロフィールを編集しました。'
                p = Profile.objects.get(user=user)
                request.session['userimage'] = p.image.url
                return redirect('users:profile_show', username)
            else:
                user_p = Profile.objects.get(user=user)
                initial_img = {
                    'image': user_p.image,
                }
                photo = forms.ProfilePhotoForm(initial=initial_img)
                message = 'プロフィール編集に失敗しました。入力値をもう一度ご確認ください。'
                context = {
                    'message': message,
                    'forms': form,
                    'username': username,
                    'photo': photo,
                    'error_msg': ''
                }
                return render(request, 'users/articles/profile_form.html', context)
    else:
        context = {
            'message': '無効なアクセスです。'
        }

    return render(request, 'users/message.html', context)

def profile_delete(request, username):
    try:
        request.session['username']
    except KeyError:
        context = {
            'message': '記事を削除するには、ログインしてください'
        }
        return render(request, 'users/message.html', context)
    else:
        pass

    user = User.objects.get(username=username)

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        request.session['message'] = 'プロフィールがありません'
        return redirect('users:profile_form')
    else:
        profile.delete()

    try:
        del request.session['userimage']
    except KeyError:
        pass

    request.session['message'] = '{}のプロフィールを削除しました。'.format(username)
    return redirect('users:profile_show', username)


def profile_show(request, user):
    user = User.objects.get(username=user)

    try:
        self_username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        pass

    # メッセージがあれば取得
    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = ''
    else:
        pass

    # ユーザーのプロフィールが登録されているかどうかを判別
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        context = {
            'username': user.username,
            'message': message,
        }
        return render(request, 'users/articles/no_profile.html', context)
    else:
        pass

    # パートナーが登録されているかチェック
    try:
        partner = User.objects.get(username=profile.partner)
    except User.DoesNotExist:
        partner = ''
        partner_username = ''
        partner_photo = ''
    else:
        partner_username = partner.username
        # 登録されていた場合、そのパートナーのプロフィール情報を取得
        try:
            partner_profile = Profile.objects.get(user=partner)
        except Profile.DoesNotExist:
            partner_photo = None
        else:
            partner_photo = partner_profile.image

    # フォロワーが存在しているかどうかをチェック
    try:
        Follow.objects.get(user__username=self_username, followed_user__username=user.username)
    except Follow.DoesNotExist:
        is_follow = False
    else:
        is_follow = True

    # 自身の書いた記事を取得
    try:
        articles = Article.objects.filter(user__username=user.username).order_by('-pk')
    except Article.DoesNotExist:
        articles = ''
    else:
        pass

    context= {
        'username': user.username,
        'ability_power': profile.ability_power,
        'ability_speed': profile.ability_speed,
        'ability_magic': profile.ability_magic,
        'ability_brain': profile.ability_brain,
        'ability_gard': profile.ability_gard,
        'ability_magicgard': profile.ability_magicgard,
        'greeting': profile.greeting,
        'partner': profile.partner,
        'photo': profile.image,
        'partner_name': partner_username,
        'partner_photo': partner_photo,
        'is_follow': is_follow,
        'message': message,
        'articles': articles,
    }

    return render(request, 'users/articles/profile.html', context)

def comment_regist(request, article_id):
    try:
        username = request.session['username']
    except KeyError:
        context = {
            'message': 'コメントを書くにはログインが必要です',
        }
        return render(request, 'users/message.html', context)
    else:
        pass

    if request.method == 'POST':
        comment = forms.CommentForm(request.POST)
        res_comment = request.POST['body']
        if comment.is_valid():
            comment_model = comment.save(commit=False)
            comment_model.article = Article.objects.get(pk=article_id)
            user = User.objects.get(username=username)
            comment_model.user = user
            comment_model.save()
            comment_id = comment_model.id
            if is_XHR:
                DOMAIN = '{0}://{1}'.format(request.scheme, request.get_host())
                str_date_without0 = get_str_date_now()
                # プロフィールが未登録のケースを想定
                try:
                    profile = Profile.objects.get(user=user)
                except Profile.DoesNotExist:
                    image_url = URL_NO_IMAGE_FACE
                else:
                    image_url = profile.image.url

                return JsonResponse({
                    'comment_xhr_response_body': res_comment,
                    'comment_xhr_response_name': username,
                    'comment_xhr_response_date': str_date_without0,
                    'comment_xhr_response_img': image_url,
                    'comment_xhr_response_a': DOMAIN + '/users/profile_show/{}'.format(username),
                    'comment_xhr_response_a_del': DOMAIN + '/users/comment_delete/{}'.format(comment_id),
                })
            else:
                return redirect('users:article_show', article_id)
        else:
            context = {
                'message': 'コメントの内容が不正です。'
            }
            return render(request, 'users/message.html', context)

def comment_delete(request, comment_id=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {
            'message': 'コメントを削除するには、本人である必要があります。'
        }
        return render(request, 'users/message.html', context)
    else:
        pass

    if comment_id:
        comment = Comment.objects.get(pk=comment_id)
        article_id = comment.article.id
        comment.delete()
        return redirect('users:article_show', id=article_id)

def reply_regist(request, comment_id=None, article_id=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {
            'message': '返信するには、ログインが必要です'
        }
        return render(request, 'users/message.html', context)
    else:
        pass

    if request.method == 'POST':
        user = User.objects.get(username=username)
        comment = Comment.objects.get(pk=comment_id)
        reply = forms.ReplyForm(request.POST)

        if reply.is_valid():
            reply_model = reply.save(commit=False)
            reply_model.user = user
            reply_model.comment = comment
            reply_model.save()
            reply_id = reply_model.id

        if is_XHR:
            profile = Profile.objects.get(user=user)
            str_date_without0 = get_str_date_now()
            DOMAIN = '{0}://{1}'.format(request.scheme, request.get_host())

            return JsonResponse({
                'reply_xhr_response_img': profile.image.url,
                'reply_xhr_response_body': request.POST['body'],
                'reply_xhr_response_date': str_date_without0,
                'reply_xhr_response_name': username,
                'reply_xhr_response_a_del': DOMAIN + '/users/reply_delete/{0}/{1}'.format(reply_id, article_id),
            })
        else:
            return redirect('users:article_show', article_id)

def reply_delete(request, reply_id=None, article_id=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {
            'message': '削除するにはログインが必要です'
        }
        return render(request, 'users/message.html', context)
    else:
        pass

    target_reply = Reply.objects.get(pk=reply_id)
    if target_reply.user.username != username:
        context = {
            'message': '自分以外のメッセージを削除することはできません',
        }
        return render(request, 'users/message.html', context)
    else:
        target_reply.delete()
        return redirect('users:article_show', article_id)


def bookmark_regist(request, article_id=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {
            'message': 'ブックマークするにはログインが必要です',
        }
        return render(request, 'users/message.html', context)
    else:
        pass

    if article_id:
        user = User.objects.get(username=username)
        article = Article.objects.get(pk=article_id)
        bookmark = Bookmark(
            user=user,
            article=article,
        )
        bookmark.save()
        return redirect('users:index')
    else:
        context = {
            'message': '記事が正しく選択されていませｎ'
        }
        return render(request, 'users/message.html', context)

def bookmark_show(request):
    try:
        username = request.session['username']
    except KeyError:
        context = {
            'message': 'ログインしてください'
        }
        return render(request, 'users/message.html', context)
    else:
        pass

    try:
        message = request.session['message']
    except KeyError:
        message = ''
    else:
        del request.session['message']

    bookmarks = Bookmark.objects.filter(user__username=username).order_by('-pk')
    context = {
        'message': message,
        'bookmarks' : bookmarks,
    }
    return render(request, 'users/articles/bookmark_show.html', context)

def bookmark_release(request):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインが必須です'}
        return render(request, 'users/message.html', context)
    else:
        pass

    if request.method == 'POST':
        release_num = request.POST.getlist('bookmark_release_check')
        for bookmark_id in release_num:
            Bookmark.objects.filter(pk=bookmark_id).delete()
        request.session['message'] = 'ブックマークを削除しました'
        return redirect('users:bookmark_show')

def album_regist(request, photo_id=None, article_id=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインが必須です'}
        return render(request, 'users/message.html', context)
    else:
        pass

    user = User.objects.get(username=username)
    photo = Photo.objects.get(pk=photo_id)
    album = Album(
        user = user,
        photo = photo,
    )
    album.save()
    return redirect('users:article_show', article_id)

def album_show(request):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインが必須です'}
        return render(request, 'users/message.html', context)
    else:
        pass

    albums = Album.objects.filter(user__username=username).order_by('-id')
    context = {
        'albums': albums,
    }
    return render(request, 'users/articles/album_show.html', context)

def album_release(request):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインが必要です'}
        return render(request, 'users/message.html', context)
    else:
        pass

    if request.method == 'POST':
        release_albums = request.POST.getlist('album_release_check')
        for release_id in release_albums:
            Album.objects.filter(pk=release_id).delete()
        return redirect('users:album_show' )


def tag_regist(request, article_id=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
    else:
        pass

    if request.method == 'POST':
        tag = forms.TagForm(request.POST)

        # 同じ記事に、同じタグが登録済されていたら、タグは追加せずにリダイレクト
        is_get = Tag.objects.filter(article__id=article_id, tag=request.POST['tag'])
        if is_get:
            return redirect('users:article_show', article_id)

        # タグが10個ついていたら、タグ追加しない
        is_over = Tag.objects.filter(article__id=article_id).count()
        if is_over >= 10:
            return redirect('users:article_show', article_id)

        if tag.is_valid():
            tag_model = tag.save(commit=False)
            tag_model.user = User.objects.get(username=username)
            tag_model.save()
            # ManytoManyFieldを保存するときは、Tagオブジェクトにidが付与されていないとだめらしい by エラーメッセージ
            article = Article.objects.filter(pk=article_id)
            tag_model.article.add(article_id)
            tag_model.save()
            return redirect('users:article_show', article_id)
        else:
            context = {'message': 'タグ登録に失敗しました'}
    else:
        context = {'message': 'アクセスが不正です'}

    return render(request, 'users/message.html' ,context)


def tag_delete(request, article_id=None):
    if request.method == 'POST':
        del_tags = request.POST.getlist('tag_del')
        for tag_id in del_tags:
            Tag.objects.get(pk=tag_id).delete()
        return redirect('users:article_show', article_id)


def tag_search(request, tag=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインが必要です'}
        return render(request, 'users/message.html', context)
    else:
        pass

    try:
        message = request.session['message']
    except KeyError:
        message = ''
    else:
        del request.session['message']

    if tag:
        # タグで紐づけた記事の取得
        # 失敗log：ManyToManyFieldのデータ取得をforでやろうとしたが、objectを拾えなかった
        #tags = Tag.objects.filter(tag=tag) #←失敗コード
        #arts = [tag.article for tag in tags]　#←失敗コード
        # ↓成功：ManyToManyの場合も、逆参照には related_name（tagged_art） を使えばよいみたいだ。
        articles = Article.objects.filter(tagged_art__tag=tag).order_by('-id')

        # タイトル画像選出：パターン１　最初に登録された写真をmain_photoに採用するコード
        #（ filterを指定する場合、そのオブジェクトは単体である必要があるようだ。なので[art_num]とした。さらに、ほしい写真は１枚なので[photo_num]で取得した。）
        #art_num = articles.count() - 1
        #photo_num = Photo.objects.filter(article=articles[art_num]).count() -1
        #main_photo = Photo.objects.filter(article=articles[art_num])[photo_num]

        # タイトル画像選出：パターン２　「１」が、もっとスマートに書けた
        #main_photo = Photo.objects.filter(article__tagged_art__tag=tag).last()

        # タグのタイトル画像選出：パターン３ 最もアルバム登録されている写真を、main_photoに選出
        # 課題：うまくかけたけれど、このロジックだと人気写真がひたすら表示され続ける可能性があるので、実務的じゃない。
        photos = Photo.objects.filter(article__tagged_art__tag=tag)
        max_cnt = 0
        main_photo = photos[0]
        for i, photo in enumerate(photos):
            if Album.objects.filter(photo=photo).count() > max_cnt:
                max_cnt = Album.objects.filter(photo=photo).count()
                main_photo = photo

        # タグのタイトル画像抽出：パターン４（記録のため、パターン３の変数を上書き）
        # 同じタグが付けられている記事のうち、最もアクセスの多い記事を抽出。
        # その中で、is_bestを選定。なければ、アルバム登録が最大の写真を main_photoに選定
        tagged_arts = Article.objects.filter(tagged_art__tag=tag).distinct()
        v_keys = []
        v_values = []
        v_max = 0
        v_art = ''
        for art in tagged_arts:
            v_keys.append(art.id)
            v_values.append(Visit.objects.filter(article=art).count())
        for i, key in enumerate(v_keys):
            if v_values[i] >= v_max:
                v_art = v_keys[i]
                v_max = v_values[i]
        best_art = Article.objects.get(pk=v_art)
        try:
            main_photo = Photo.objects.get(article=best_art, is_best=True)
        except Photo.DoesNotExist:
            main_photo = Photo.objects.filter(article=best_art).last()
        else:
            pass

        # タグの説明取得（タグ情報が複数存在していたケースを想定し、常に最新版を取得する）
        tag_detail = TagDetail.objects.filter(tag_str=tag).last()

        # タグ情報が存在し、画像が登録されていれば、main_photo はそっちを使う。
        if tag_detail:
            try:
                p = Photo.objects.get(image=tag_detail.image.image)
            except Photo.DoesNotExist:
                pass
            else:
                main_photo = p
        else:
            tag_detail = ''

        # Articieの写真抽出
        photos = []
        for art in articles:
            is_photo_selected = False
            art_photos = Photo.objects.filter(article=art.id)
            for art_photo in art_photos:
                if art_photo.is_best:
                    photos.append(art_photo)
                    is_photo_selected = True
                    break
            if not is_photo_selected:
                photos.append(Photo.objects.filter(article=art.id).first())

        # ブックマーク情報
        bookmarks = Bookmark.objects.filter(user__username=username)

        # 人気記事として、アクセスの多い順に記事を取得
        art_pvs = []
        art_ids = []
        populer_articles = []
        populer_photos = []
        art_limit = 100

        # 記事取得（ただし、検索結果にて既に表示されている記事は除外）
        article_ids = Article.objects.values_list('id').filter(tagged_art__tag=tag).order_by('-id')
        all_arts = Article.objects.exclude(id__in=article_ids)
        for art in all_arts:
            art_pvs.append(Visit.objects.filter(article=art.id).count())
            art_ids.append(art.id)
        pop_arts_dict = dict(zip(art_ids, art_pvs))
        pop_arts_dict = sorted(pop_arts_dict.items(), key = lambda x:x[1], reverse=True)

        # 記事に紐づく写真も取得
        for i, art_id_pv in enumerate(pop_arts_dict):
            is_best_exists = False
            populer_articles.append(Article.objects.get(pk=art_id_pv[0]))
            pop_photos = Photo.objects.filter(article__id=art_id_pv[0])
            # is_bestを探して、見つかればそれを取得。見つからなければ、登録された最初の写真を取得。
            for i, pop_photo in enumerate(pop_photos):
                if i == 0:
                    temporary_photo_first = pop_photo
                if pop_photo.is_best:
                    temporary_photo_is_best = pop_photo
                    is_best_exists = True
                if i == pop_photos.count() - 1:
                    if is_best_exists:
                        populer_photos.append(temporary_photo_is_best)
                    else:
                        populer_photos.append(temporary_photo_first)
            if i > art_limit:
                break


        # タグの編集権限
        is_editable = True

        context = {
            'main_photo': main_photo, # タグの説明写真
            'photos': photos, # Articlesの代表写真
            'tag': tag,
            'articles': articles,
            'bookmarks': bookmarks,
            'is_XHR': is_XHR,
            'message': message,
            'tag_detail': tag_detail,
            'is_editable' : is_editable,
            'populer_articles': populer_articles,
            'populer_photos': populer_photos,
        }
        return render(request, 'users/articles/index.html', context)
    else:
        return redirect('users:index')

def article_search(request):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        pass

    try:
        message = request.session['message']
    except KeyError:
        message = ''
    else:
        del request.session['message']

    if request.method == 'POST':
        text = request.POST['search_text']

        if text == '':
            return redirect('users:index')

        tags = text.split()

        # 検索ワードによる記事検索：タグを検索
        queries = []
        query_sets = []
        for tag in tags:
            query_sets = Article.objects.filter(tagged_art__tag__contains=tag)
            query_sets = query_sets.order_by('-pk')
            for query_set in query_sets:
                queries.append(query_set)

        # 検索ワードによる記事検索：タイトルを検索
        for tag in tags:
            query_sets = Article.objects.filter(title__icontains=tag)
            for query_set in query_sets:
                queries.append(query_set)

        # レコードの重複を削除
        # articles = set(queries) # この方法でも重複削除できるが、順序が変わってしまう。
        articles = dict.fromkeys(queries)

        # お気に入り登録取得
        bookmarks = Bookmark.objects.filter(user__username=username)

        # 記事の写真：is_bestか、最初に登録された写真を採用
        photos = []
        for art in articles:
            is_photo_selected = False
            for photo in Photo.objects.filter(article=art.id):
                if not is_photo_selected and photo.is_best:
                    photos.append(photo)
                    is_photo_selected = True
            if not is_photo_selected:
                photos.append(Photo.objects.filter(article=art.id).first())

        # タグの写真：タグ写真に選ばれているものがあればそれを採用。
        try:
            tag_d_last = TagDetail.objects.filter(tag_str=text).last()
            main_photo = Photo.objects.filter(tag_image=tag_d_last.id).last()
        except AttributeError:
            main_photo = ''
        else:
            pass

        # タグの写真：選ばれている写真がなければ、タグで紐づいているか、もしくは似ているタグの記事のうち、最もアクセスの多い記事の代表写真 or lastを採用。
        if not main_photo:
            pv = []
            max_pv = 0
            max_pv_art = ''
            for tag in tags:
                tag_arts = Article.objects.filter(tagged_art__tag__icontains=tag)
                for tag_art in tag_arts:
                    pv = Visit.objects.filter(article=tag_art.id).count()
                    if max_pv < pv:
                        max_pv_art = tag_art
            if max_pv_art:
                is_best_selected = False
                art_photos = Photo.objects.filter(article=max_pv_art)
                for art_photo in art_photos:
                    if art_photo.is_best:
                        main_photo = art_photo
                        is_best_selected = True
                if not is_best_selected:
                    main_photo = Photo.objects.filter(article=max_pv_art).last()

        # タグの詳細情報を取得。タグの詳細情報は何度も更新されて複数存在するので、last で取得
        tag_detail = TagDetail.objects.filter(tag_str=text).last()

        # 人気の記事：ブックマークの多い順（ただし、すでに表示される記事は除外）
        selected_art_ids = []
        bk_cnts = []
        bk_art_ids = []
        populer_articles = []
        for art in articles:
            selected_art_ids.append(art.id)

        bk_arts = Article.objects.exclude(pk__in=selected_art_ids)
        for bk_art in bk_arts:
            bk_cnts.append(Bookmark.objects.filter(article__id=bk_art.id).count())
            bk_art_ids.append(bk_art.id)

        bk_arts_dict = dict(zip(bk_art_ids, bk_cnts))
        bk_arts_dict = sorted(bk_arts_dict.items(), key=lambda x:x[1], reverse=True)
        for bk_art_dict in bk_arts_dict:
            populer_articles.append(Article.objects.get(pk=bk_art_dict[0]))

        # 人気の記事：写真取得（ ルールは Index流。 is_best > first_selected で、代表写真を１枚を Viewから選ぶ。）
        populer_photos = []
        for bk_art_id in bk_art_ids:
            is_best_selected = False
            bk_art_photos = Photo.objects.filter(article__id=bk_art_id)
            for i, bk_art_photo in enumerate(bk_art_photos):
                # まず、firstを保存しておく
                if i == 0 :
                    pp_temporary_first = bk_art_photo
                # 初めて hitした is_bestも保存
                if not is_best_selected and bk_art_photo.is_best:
                    pp_temporary_is_best = bk_art_photo
                    is_best_selected =True
                # Loop最後に、is_bestがなければ firstを。そうでなければ is_bestを保存
                if i == bk_art_photos.count()-1:
                    if is_best_selected:
                        populer_photos.append(pp_temporary_is_best)
                    else:
                        populer_photos.append(pp_temporary_first)

        # サーチから来た場合は、タグ情報を編集できないようにする
        is_editable = False

        context = {
            'tag_detail': tag_detail,
            'tag': text,
            'main_photo': main_photo,
            'photos': photos,
            'articles': articles,
            'bookmarks': bookmarks,
            'is_editable': is_editable,
            'is_XHR': is_XHR,
            'populer_articles': populer_articles,
            'populer_photos': populer_photos,
        }
        return render(request, 'users/articles/index.html', context)


def follow_regist(request, followed_username=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        pass

    if followed_username == username:
        request.session['message'] = '自分自身はフォローできません'
        return redirect('users:profile_show', followed_username)

    try:
        followed_user = Follow.objects.get(user__username=username, followed_user__username=followed_username)
    except Follow.DoesNotExist:
        follow = Follow(
            user = User.objects.get(username=username),
            followed_user = User.objects.get(username=followed_username)
        )
        follow.save()
        request.session['message'] = 'フォローしました'
        return redirect('users:profile_show', followed_username)
    else:
        context = {'message': 'すでにフォローしています'}
        return render(request, 'users/message.html', context)


def follow_release(request, followed_username=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        pass

    Follow.objects.filter(user__username=username, followed_user__username=followed_username).delete()
    request.session['message'] = 'フォローを解除しました'
    return redirect('users:profile_show', followed_username)


def good_regist(request, article_id=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        pass

    try:
        Good.objects.get(user__username=username, article__id=article_id)
    except Good.DoesNotExist:
        good = Good(
            user = User.objects.get(username=username),
            article = Article.objects.get(pk=article_id),
        )
        good.save()
        good_cnt = Good.objects.filter(article__id=article_id).count()
        return JsonResponse({
            'good_cnt': good_cnt,
        })
    else:
        context = {'message': 'すでにいいねしています'}
        return render(request, 'users/message.html', context)

def good_release(request, article_id=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        pass

    try:
        good = Good.objects.get(user__username=username, article__id=article_id)
    except Good.DoesNotExist:
        return redirect('users:article_show', article_id)
    else:
        good.delete()
        good_cnt = Good.objects.filter(article__id=article_id).count()
        return JsonResponse({
            'good_cnt': good_cnt,
        })


def visit_count(request, article_id=None):
    try:
        username = request.session['username']
    except KeyError:
        user = ''
    else:
        user = User.objects.get(username=username)

    visit = Visit(
        user = user,
        article = Article.objects.get(pk=article_id)
    )
    visit.save()
    visit_cnt = Visit.objects.filter(article__id=article_id).count()
    return JsonResponse({
        'visit_cnt':  visit_cnt,
    })


def tag_detail_regist_form(request, tag=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        pass

    # タグ情報の存在を調べる
    tag_detail = TagDetail.objects.filter(tag_str=tag).last()
    # タグ情報登録済み（編集）の場合
    if tag_detail:
        initial_dict = {
            'image': tag_detail.image,
            'detail': tag_detail.detail,
        }
        t_form = forms.TagDetailForm(tag=tag, initial=initial_dict)
    # タグ情報未登録（新規登録）の場合
    else:
        t_form = forms.TagDetailForm(tag=tag)

    context = {
        't_form': t_form,
        'tag': tag,
    }
    return render(request, 'users/articles/tag_detail_regist_form.html', context)


def tag_detail_regist(request, tag=None):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        pass

    if request.method == 'POST':
        tag_detail = forms.TagDetailForm(tag=tag, data=request.POST)
        if tag_detail.is_valid():
            tag_detail_model = tag_detail.save(commit=False)
            tag_detail_model.user = User.objects.get(username=username)
            tag_detail_model.tag_str = tag
            tag_detail_model.save()
            request.session['message'] = '「{}」の説明を更新しました。'.format(tag)
            return redirect('users:tag_search', tag)
        else:
            t_form = tag_detail
            context = {
                'message': '登録に失敗しました。入力フォームを確認してください。',
                't_form': t_form,
                'tag': tag,
            }
            return render(request, 'users/articles/tag_detail_regist_form.html', context)


# 2021.5.8 本番反映完了により、こちらのテストは Close（本番用は def index に記載）
def analysis_test(request):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        pass

    # TRY1：Userがアクセスしたことのあるタグ
    visits = Visit.objects.filter(user__username=username).values('article__tagged_art__tag').distinct()
    tags = []
    for visit in visits:
        tags.append(visit['article__tagged_art__tag'])

    # TRY2：そのタグのアクセス総数
    pvs = []
    for tag in tags:
        pvs.append(Visit.objects.filter(article__tagged_art__tag=tag, user__username=username).count())

    # TRY3：タグをアクセス順に並べる（タグ Noneは常に未訪問状態と同等に扱う）
    tag_dict = dict(zip(tags, pvs))
    tag_dict = sorted(tag_dict.items(), key = lambda x:x[1], reverse=True)
    tags = []
    for tag in tag_dict:
        if tag[0] == None:
            pass
        else:
            tags.append(tag[0])

    # TRY4：アクセスしたことのないタグも追加
    e_tags_dict = Tag.objects.exclude(tag__in=tags).values('tag').distinct()
    e_tags = []
    for e_tag in e_tags_dict:
        e_tags.append(e_tag['tag'])

    # TRY5：アクセスの多いタグ順に記事を取得したいが、きれいじゃない。意図しない並び順になる。
    tag_all = tags + e_tags
    arts = Article.objects.filter(tagged_art__tag__in=tag_all).distinct()
    arts_tag_none = Article.objects.filter(tagged_art__tag=None).distinct()

    # TRY6：アクセスの多いタグ順に記事取得
    art_objs = []
    for t in tag_all:
        art_objs.append(Article.objects.filter(tagged_art__tag=t).order_by('-pk'))
    art_objs.append(Article.objects.filter(tagged_art__tag__isnull=True).order_by('-pk'))

    # TRY7：6の重複記事を削除
    art_all = []
    for art_queryset in art_objs:
        for art in art_queryset:
            art_all.append(art)
    art_all = sorted(set(art_all), key=art_all.index)
    art_cnt = len(art_all)

    context = {
        'values': tag_dict,
        'values2': tags,
        'values3': e_tags,
        'values4': tag_all,
        'articles': arts,
        'articles_tag_none': arts_tag_none,
        'art_objs': art_objs,
        'art_all': art_all,
        'art_cnt': art_cnt,
        'username': username,
    }
    return render(request, 'users/articles/_analysis_test.html', context)
# 2021.5.12 本番への移行に伴い、こちらのテストは Close （本番は Profile_form ）
def slider_test(request):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        user = User.objects.get(username=username)

    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        p_form = forms.Profile(user=user)
    else:
        initial_dict = {
            'ability_power': profile.ability_power,
            'ability_speed': profile.ability_speed,
            'ability_gard': profile.ability_gard,
            'ability_magic': profile.ability_magic,
            'ability_brain': profile.ability_brain,
            'ability_magicgard': profile.ability_magicgard,
            'greeting': profile.greeting,
            'partner': profile.partner,
        }
        p_form = forms.Profile(user=user ,initial=initial_dict)

    context = {
        'forms': p_form,
        'username': username,
    }
    return render(request, 'users/articles/_slider_test.html', context)

def article_form_with_tags_test(request):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        pass

    a_forms = forms.ArticleForm()
    photoForms = modelformset_factory(
        model = Photo,
        fields = ('image', ),
        extra = article_photo_form_cnt
    )
    p_forms = photoForms(queryset=Photo.objects.none())

    context = {
        'a_forms': a_forms,
        'p_forms': p_forms,
    }
    return render(request, 'users/articles/_article_form_with_tags_test.html', context)

def article_regist_with_tags_test(request):
    try:
        username = request.session['username']
    except KeyError:
        context = {'message': 'ログインしてください'}
        return render(request, 'users/message.html', context)
    else:
        pass

    if request.method == 'POST':
        tags = request.POST.getlist('tags[]')

    context = {
        'tags': tags,
    }

    return render(request, 'users/articles/_temporary_test.html', context)

def cover_image_preview_test(request):
    photos = Photo.objects.all().order_by('?')[0:100]
    context = {
        'photos': photos,
    }
    return render(request, 'users/articles/_cover_image_preview_test.html', context)