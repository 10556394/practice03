from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('', views.index, name='index'),

    # 作業用の便利機能
    path('todo/', views.todo_show, name='todo_show'),
    path('show_all_user/', views.show_all_user, name='show_all_user'),

    # ユーザー登録関連
    path('user_form/', views.user_form, name='user_form'),
    path('main_regist/<token>', views.main_regist, name='main_regist'),
    path('regist_user_info/<uuid>', views.regist_user_info, name='regist_user_info'),

    # 詳細表示
    #path('user_list/', views.user_list, name='user_list'),
    path('list_view_test/', views.ListViewTest.as_view(), name='list_view_test'),
    path('detail_view_test/<str:pk>', views.DetailViewTest.as_view(), name='detail_view_test'),

    # パスワードを変更
    path('change_password/', views.ChangePassword.as_view(), name='change_password'),
    path('change_password/complete/', views.ChangePasswordComplete.as_view(), name='change_password_complete'),

    # パスワードを忘れた場合
    #path('reset_password/', views.reset_password, name='reset_password'),
    path('reset_password2/', views.ResetPassword.as_view(), name='reset_password2'),
    path('reset_password2/done/', views.ResetPasswordDone.as_view(), name='reset_password2_done'),
    path('reset_password2/confirm/<str:uidb64>/<str:token>/', views.ResetPasswordConfirm.as_view(), name='reset_password2_confirm'),
    path('reset_password2/complete/', views.ResetPasswordComplete.as_view(), name='reset_password2_complete'),

    # ログイン・アウト
    path('logout', views.logout, name='logout'),
    path('login', views.login, name='login'),
    path('login2', views.Login2.as_view(), name='login2'),
    path('login3', views.Login3.as_view(), name='login3'),
    path('logout2', views.Logout2.as_view(), name='logout2'),

    # マイページ
    path('my_page', views.my_page, name='my_page'),

    # 記事投稿～修正・削除
    path('article_form/', views.article_form, name='article_form'), # 不具合が見つかったため、ver2に以降
    path('article_form2/', views.article_form2, name='article_form2'),
    path('article_regist/', views.article_regist, name='article_regist'), # 不具合が見つかったため、ver2に以降
    path('article_regist2/', views.article_regist2, name='article_regist2'),
    path('article_show/<int:id>', views.article_show, name='article_show'),
    path('show_my_article_list/', views.show_my_article_list, name='show_my_article_list'),
    path('article_edit/<int:id>', views.article_edit, name='article_edit'),
    path('article_edit_run/<int:id>', views.article_edit_run, name='article_edit_run'),
    path('article_delete/<int:id>', views.article_delete, name='article_delete'),
    path('article_search', views.article_search, name='article_search'),

    # プロフィール CRUD
    path('profile_form/', views.profile_form, name='profile_form'),
    path('profile_show/<str:user>', views.profile_show, name='profile_show'),
    path('profile_regist/', views.profile_regist, name='profile_regist'),
    path('profile_delete/<str:username>', views.profile_delete, name='profile_delete'),

    # コメント
    path('comment_regist/<int:article_id>', views.comment_regist, name='comment_regist'),
    path('comment_delete/<int:comment_id>', views.comment_delete, name='comment_delete'),

    # コメント返信
    path('reply_regist/<int:comment_id>/<int:article_id>', views.reply_regist, name='reply_regist'),
    path('reply_delete/<int:reply_id>/<int:article_id>', views.reply_delete, name='reply_delete'),

    # お気に入り（ブックマーク）
    path('bookmark_regist/<int:article_id>', views.bookmark_regist, name='bookmark_regist'),
    path('bookmark_show/', views.bookmark_show, name='bookmark_show'),
    path('bookmark_release', views.bookmark_release, name='bookmark_release'),

    # マイアルバム（画像ブックマーク）
    path('album_regist/<int:photo_id>/<int:article_id>', views.album_regist, name='album_regist'),
    path('album_show/', views.album_show, name='album_show'),
    path('album_release', views.album_release, name='album_release'),

    # タグ
    path('tag_regist/<int:article_id>', views.tag_regist, name='tag_regist'),
    path('tag_delete/<int:article_id>', views.tag_delete, name='tag_delete'),
    path('tag_search/<str:tag>', views.tag_search, name='tag_search'),
    path('tag_detail_regist_form/<str:tag>', views.tag_detail_regist_form, name='tag_detail_regist_form'),
    path('tag_detail_regist/<str:tag>', views.tag_detail_regist, name='tag_detail_regist'),

    # フォロー
    path('follow_regist/<str:followed_username>', views.follow_regist, name='follow_regist'),
    path('follow_release/<str:followed_username>', views.follow_release, name='follow_release'),
    path('show_follow_user/', views.show_follow_user, name='show_follow_user'),

    # いいね
    path('good_regist/<int:article_id>', views.good_regist, name='good_regist'),
    path('good_release/<int:article_id>', views.good_release, name='good_release'),

    # アクセス
    path('visit_count/<int:article_id>', views.visit_count, name='visit_count'),

    # テスト（試行錯誤のテスト用。本番には使わない）
    path('analysis_test/', views.analysis_test, name='analysis_test'),
    path('slidet_test/', views.slider_test, name='slider_test'),
    path('article_form_with_tags_test/', views.article_form_with_tags_test, name='article_form_with_tags_test'),
    path('article_regist_with_tags_test/', views.article_regist_with_tags_test, name="article_regist_with_tags_test"),
    path('cover_image_preview_test/', views.cover_image_preview_test, name='cover_image_preview_test'),
]
