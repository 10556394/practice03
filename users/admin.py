from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext, gettext_lazy as _
from django import forms
from django.utils.safestring import mark_safe

# Register your models here.

class PhotoInline(admin.StackedInline):
    model = models.Photo
    extra = 3

@admin.register(models.Department)
class AdminDepartment(admin.ModelAdmin):
    pass

@admin.register(models.User)
class AdminUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'email', 'departments')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Improtant dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'pk',  'email', 'full_name', 'is_staff', 'is_active')
    search_fields = ('username', 'full_name', 'email')
    filter_horizontal = ('groups', 'user_permissions', 'departments')

@admin.register(models.Profile)
class AdminProfile(admin.ModelAdmin):
    pass

@admin.register(models.Article)
class AdminAtricle(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'posted_date')
    inlines = [PhotoInline]

@admin.register(models.Comment)
class AdminComment(admin.ModelAdmin):
    list_display = ('user','article', 'body', 'posted_date')

@admin.register(models.Reply)
class AdminReply(admin.ModelAdmin):
    list_display = ('user', 'comment', 'body', 'posted_date')

@admin.register(models.Bookmark)
class AdminBookmark(admin.ModelAdmin):
    list_display = ('user', 'article', 'bookmarked_date')

@admin.register(models.Album)
class AlbumAdmin(admin.ModelAdmin):
    def image_view(self, obj):
        return mark_safe('<img src="{}" style="width:100px; height:100px; object-fit:cover;">'.format(obj.photo.image.url))
    list_display = ('user', 'image_view', 'regist_date')

@admin.register(models.Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ('user', 'tag', 'articles', 'tagged_date')
    def articles(self, obj):
        return '\n'.join([p.title for p in obj.article.all()])

@admin.register(models.Follow)
class AdminFollow(admin.ModelAdmin):
    list_display = ('user', 'followed_user', 'followed_date')

@admin.register(models.Good)
class AdminGood(admin.ModelAdmin):
    list_display = ('user', 'article', 'liked_date')

@admin.register(models.TagDetail)
class AdminTagDetail(admin.ModelAdmin):
    list_display = ('user', 'tag', 'tag_str', 'detail', 'image', 'write_date')