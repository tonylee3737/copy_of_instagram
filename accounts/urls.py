from django.urls import path, include
from rest_framework_jwt.views import verify_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import obtain_jwt_token
from django.urls import path, re_path
from accounts import views


app_name = 'accounts'
urlpatterns = [
    path('signup_serializer/', views.SignupView.as_view(), name='login'),
    # 다른 웹에서 호출을 하면(http://localhost:8000/accounts/signup/ username=tony password='pass') 뷰단에서 입력된 메소드대로 회원가입이 이루어진다.

    path('token/', obtain_jwt_token),
    path('token/refresh/', refresh_jwt_token),
    path('token/verify/', verify_jwt_token),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('profile/', views.root, name='root'),
    path('logout/', views.logout, name='logout'),
    path('edit/', views.edit, name='edit'),
    path('password_change/', views.password_change, name='password_change'),
    # 팔로우 언팔로우하기.
    re_path(r'^(?P<username>[\w.@+-]+)/follow/$',
            views.user_follow, name='user_follow'),
    re_path(r'^(?P<username>[\w.@+-]+)/unfollow/$',
            views.user_unfollow, name='user_unfollow'),

]
