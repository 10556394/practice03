from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
import uuid as uuid_lib
from django.core.exceptions import ValidationError

class Department(models.Model):
    name = models.CharField(_('所属'), max_length=150, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('所属')
        verbose_name_plural = _('所属')


class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(default=uuid_lib.uuid4, primary_key=True, editable=False)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 charactors or fewer. Letters, digits and @/./+/-/_ only.'),
        validators = [username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    full_name = models.CharField(_('氏名'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True, unique=True)
    departments = models.ManyToManyField(
        Department,
        verbose_name=_('所属'),
        blank=True,
        help_text=_('Specific Departments for this user.'),
        related_name='user_set',
        related_query_name='user',
    )
    is_staff=models.BooleanField(
        _('staff status'),
        default=True,
        help_text=_('Disignates whether the user can log into this admin site.'),
    )
    is_active=models.BooleanField(
        _('active'),
        default = True,
        help_text=_(
            'Designates whether this user should be treated as active.'
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', ]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clearn(self):
        super().clearn()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name


def check_ability(value):
    if value < 0 or value > 10:
        raise ValidationError('0 ～ 10で選んでください><')

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name = 'person'
    )
    image = models.ImageField(
        verbose_name = 'image',
        upload_to = 'images/',
        null = True,
        default = 'images/no_image_face.png'
    )
    # ability_power だけは、Validator を記載していないが、form で同様のバリデーションがかけられる。
    # 挙動確認のため、この形のまま残す。
    ability_power = models.IntegerField(default=0)
    ability_speed = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    ability_brain = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    ability_magic = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    ability_gard = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    ability_magicgard = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    partner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    greeting = models.TextField(max_length=1000)
    regist_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        u = User.objects.get(username=self.user)
        return u.username

    class Meta:
        verbose_name = _('プロフィール')
        verbose_name_plural = _('プロフィール')


class Article(models.Model):
    title = models.CharField(max_length=25)
    body = models.TextField(max_length=500)
    posted_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('記事')
        verbose_name_plural = _('記事')

    def __str__(self):
        return self.title


class Photo(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name = 'art_image'
    )
    image = models.ImageField(
        verbose_name = 'image',
        upload_to = 'images/',
        null = True,
    )
    is_best = models.BooleanField(
        default = False,
        null = True,
    )
    def __str__(self):
        return self.image.url

    class Meta:
        verbose_name = _('写真')
        verbose_name_plural = _('写真')

class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete = models.CASCADE,
        related_name = 'commented_article'
    )
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
    )
    body = models.TextField(max_length=25)
    posted_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('コメント')
        verbose_name_plural = _('コメント')

    def __str__(self):
        return self.body


class Reply(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete = models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
    )
    body = models.TextField(max_length=25)
    posted_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('返信')
        verbose_name_plural = _('返信')


class Bookmark(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
    )
    article = models.ForeignKey(
        Article,
        on_delete = models.CASCADE,
        related_name = 'bookmarked_article',
    )
    bookmarked_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('ブックマーク')
        verbose_name_plural = _('ブックマーク')


class Album(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
    )
    photo = models.ForeignKey(
        Photo,
        on_delete = models.CASCADE,
        related_name = 'albumed_photo',
    )
    regist_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('アルバム')
        verbose_name_plural = _('アルバム')


class Tag(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
    )
    article = models.ManyToManyField(
        Article,
        related_name = 'tagged_art',
    )
    tag = models.TextField(max_length = 30, null=True)
    is_lock = models.BooleanField(
        default = False,
    )
    tagged_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('タグ')
        verbose_name_plural = _('タグ')

    def __str__(self):
        return self.tag


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = 'follow_user',
    )
    followed_user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = 'followed_user',
    )
    followed_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('フォロー')
        verbose_name_plural = _('フォロー')

    def __str__(self):
        return self.user

class Good(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = 'like_user',
    )
    article = models.ForeignKey(
        Article,
        on_delete = models.CASCADE,
        related_name = 'liked_article',
    )
    liked_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('いいね')
        verbose_name_plural = _('いいね')

    def __str__(self):
        return self.user

class Visit(models.Model):
    user = models.ForeignKey(
        User,
        null = True,
        blank = True,
        on_delete = models.CASCADE,
        related_name = 'visit_user',
    )
    article = models.ForeignKey(
        Article,
        on_delete = models.CASCADE,
        related_name = 'visited_article',
    )
    viewed_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('訪問')
        verbose_name_plural = _('訪問')

    def __str__(self):
        return self.user


class TagDetail(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = 'tag_detail_write_user',
    )
    # DB作成時の失敗カラム。タグは名前（文字列）で作らないといけなかった。そうしないと、同じ名前のタグと複数リレーションすることになってしまう
    tag = models.ForeignKey(
        Tag,
        on_delete = models.CASCADE,
        related_name = 'detail_writed_tag',
        null = True,
        blank = True,
    )
    tag_str = models.CharField(
        max_length = 30,
        null = True,
    )
    image = models.ForeignKey(
        Photo,
        on_delete = models.CASCADE,
        related_name = 'tag_image'
    )
    detail = models.TextField(max_length=500)
    write_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('タグ詳細')
        verbose_name_plural = _('タグ詳細')

    def __str__(self):
        return self.tag