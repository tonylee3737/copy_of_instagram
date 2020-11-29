from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from accounts.models import User  # Create your views here.
from accounts.serializers import SignupSerializer, SuggestSerializer
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView, ListAPIView, get_object_or_404
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from accounts.form import SignupForm, EditForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.views import (
    LoginView, logout_then_login, PasswordChangeView as AuthPasswordChangeView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login as auth_login
from django.urls import reverse_lazy
from accounts.models import User
# login = LoginView.as_view(template_name='accounts/login.html', LOGIN_REDIRECT_URL='accounts/login')

from django.http import HttpResponseRedirect

from django.utils.decorators import method_decorator

class LoginViewTest(LoginView):
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        messages.success(self.request, "로그인 성공!")
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())


login = LoginViewTest.as_view()
# settings LOGIN_REDIRECT_URL , django conf, global settings -> login_url , login_redirect_url 참고


def logout(request):
    messages.success(request, "로그아웃 되었습니다.")
    return logout_then_login(request)


def root(request):
    return redirect('root')


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            signed_user = form.save()
            auth_login(request, signed_user)
            messages.success(request, "회원가입을 축하합니다")
            # signed_user.send_welcome_email()
            # FIXME: Celery로 처리해보기
            return redirect('root')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


def edit(request):
    if request.method == "POST":
        post_Form = EditForm(request.POST, request.FILES,
                             instance=request.user)
        if post_Form.is_valid():
            post_Form.save()
            return redirect('root')
        else:
            return render(request, 'accounts/edit.html', {'form': post_Form})
    else:
        form = EditForm(instance=request.user)
        return render(request, 'accounts/edit.html', {'form': form})


class PasswordChangeView(LoginRequiredMixin, AuthPasswordChangeView):
    success_url = reverse_lazy('accounts:root')  # reverse_lazy?
    template_name = 'accounts/password_change_form.html'
    form_class = PasswordChangeForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "비밀번호가 변경되었습니다.")
        return super().form_valid(form)

    # def get_success_url(self):
        # , kwargs={'pk': self.object.pk,'slug':self.object.slug })
        # return reverse('accounts:root') # success_url을 사용하는 것이 좋다...?


# 반환값이 response이기 때문에 필히 반환해주어야 한다.


password_change = PasswordChangeView.as_view()


def user_follow(request, username):
    follow_user = get_object_or_404(User, username=username)
    request.user.following_set.add(follow_user)
    follow_user.follower_set.add(request.user)
    messages.success(request, f'{follow_user}님을 팔로우하였습니다.')

# http_referer 이전 경로의 주소값을 불러다준다. 경로 값이 없을 경우는 root 지정
    redirect_url = request.META.get("HTTP_REFERER", "root")
    return redirect(redirect_url)


def user_unfollow(request, username):
    unfollow_user = get_object_or_404(User, username=username)
    request.user.following_set.remove(unfollow_user)
    unfollow_user.follower_set.remove(request.user)
    messages.success(request, f'{unfollow_user}님을 언팔로우하였습니다.')
    redirect_url = request.META.get("HTTP_REFERER", 'root')
    return redirect(redirect_url)


# , SuggestionSerializer


class SignupView(CreateAPIView):  # CreateAPIView는 get method는 not allowed/ POST is allowed
    model = get_user_model()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]
# 다른 웹에서 호출 시, 이행되는 메소드, createAPI이기 때문에 get으로 요청이 오면 에러
# http POST http://localhost:8000/accounts/signup/ username = "" password = "" 라고 요청을 보냄,, 중복확인까지 가능.


class SuggestListView(ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = SuggestSerializer

    def get_queryset(self):
        qs = super().get_queryset()\
            .exclude(pk=self.request.user.pk)\
            .exclude(pk__in=self.request.user.following_set.all())
        return qs

    # http http://localhost:8000/accounts/suggest/
    # listView 는 쿼리셋을 쿼리셋이 필요하다....그래서 queryset 반면 모델은?  필요없는듯?


# 팔로우 요청 시,
@api_view(['POST'])
def follow(request):
    username = request.data['username']
    follow_user = get_object_or_404(User, username=username, is_active=True)
    request.user.following_set.add(follow_user)
    follow_user.follower_set.add(request.user)
    return Response(status.HTTP_204_NO_CONTENT)

# http POST http://localhost:8000/accounts/follow/ username=tony "Authorization=JWT key"
# 기존 로그인 된 유저에서 팔로우할 유저이름을 적고 JWT로 토큰인증


@api_view(['POST'])
def unfollow(request):
    username = request.data['username']
    follow_user = get_object_or_404(User, username=username, is_active=True)
    request.user.following_set.remove(follow_user)
    follow_user.follower_set.remove(request.user)
    return Response(status.HTTP_204_NO_CONTENT)
