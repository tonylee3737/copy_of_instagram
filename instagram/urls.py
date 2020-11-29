from django.urls import path, re_path, include
from instagram import views




app_name = 'instagram'
urlpatterns = [
    path('', views.index, name='index'),
    path('post_new/', views.post_new, name='post_new'),
    path('post/<int:pk>', views.post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('post/<int:pk>/dislike', views.post_dislike, name='post_dislike'),
    path('post/<int:pk>/like', views.post_like, name='post_like'),
    path('post/reply/<int:post_pk>/', views.post_reply, name='post_reply'),
    path('post/comment_edit/<int:comment_pk>/<int:post_pk>',
         views.comment_edit, name='comment_edit'),
    path('post/comment_delete/<int:comment_pk>/<int:post_pk>/',
         views.comment_delete, name='comment_delete'),
    re_path(r'^(?P<username>[\w.@+-]+)/$', views.user_page, name='user_page'),
    path('post/look_user/', views.look_user, name='look_user'),
    path('post/recent_feed/', views.recent_feed, name='recent_feed'),
]


# <post_id> view단에서 활용 ..// <post_id>\d -> 뒤에 숫자가 온다는 의미
