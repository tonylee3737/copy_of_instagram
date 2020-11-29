from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from instagram.models import Post, Comment
from instagram import serializers
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import render
from rest_framework.generics import get_object_or_404
from django.urls import reverse
from instagram.models import Comment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from instagram.forms import PostForm, CommentForm
from django.contrib import messages
from instagram.models import Post, Tag
from django.contrib.auth import get_user_model
from instagram.models import Post
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
# Create your views here.

from django.core.paginator import Paginator


@login_required
def index(request):
    if request.method == "POST":
        q = request.POST.get('q', '')
        post_list = Post.objects.all().filter(caption__icontains=q)

    else:
        timesince = timezone.now() - timedelta(days=30)
        post_list = Post.objects.all()\
            .filter(
                Q(author=request.user) |
                Q(author__in=request.user.following_set.all())
        )\
            .filter(
                created_at__gte=timesince)
    suggested_list = get_user_model().objects.all()\
        .exclude(pk=request.user.pk)\
        .exclude(pk__in=request.user.following_set.all())  # [:3]

    paginator = Paginator(post_list, 3)
    if request.GET.get('page') == None:
        page = 1
    else:
        page = request.GET.get('page')
    post_list = paginator.get_page(page)
    comment_form = CommentForm()
    return render(request, 'instagram/index.html', {
        'suggested_list': suggested_list,
        'post_list': post_list,
        'comment_form': comment_form,
        'paginator': paginator,
        'page': page,
    })


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            post.tag_set.add(*post.extract_caption())

            messages.success(request, '포스팅에 성공하셨습니다.')

            # root로 이동 Toto : get_absolute_url
            return redirect('accounts:root')
    else:
        form = PostForm
    return render(request, 'instagram/post_form.html', {'form': form})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comment_form = CommentForm()
    return render(request, 'instagram/post_detail.html', {
        'post': post,
        'comment_form': comment_form
    })


def comment_edit(request, comment_pk, post_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    form = CommentForm(instance=comment)
    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        form.save()
        return redirect('instagram:post_detail', pk=post_pk)
    else:
        return render(request, 'instagram/comment_edit.html', {
            'form': form,
            'comment_pk': comment_pk,
            'post_pk': post_pk,
        })


def comment_delete(request, comment_pk, post_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    comment.delete()
    return redirect('instagram:post_detail', pk=post_pk)


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = PostForm(instance=post)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post.tag_set.add(*post.extract_caption())
            messages.success(request, '포스팅에 수정완료하였습니다.')
            form.save()
    
        return redirect('instagram:index')
    else:
        return render(request, 'instagram/post_edit.html', {
            'form': form
        })


def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    messages.success(request, '포스팅을 삭제하였습니다.')
    return redirect('instagram:index')


def user_page(request, username):
    page_user = get_object_or_404(
        get_user_model(), username=username, is_active=True)
    # page_user = get_user_model().all.
    # filter(user=username)
    post_list = Post.objects.filter(author=page_user)
    post_list_count = post_list.count()
    follower = page_user.follower_set.count()
    following = page_user.following_set.count()
    if request.user.is_authenticated:
        is_follow = request.user.following_set.all().filter(pk=page_user.pk).exists()
    else:
        is_follow = False

    return render(request, 'instagram/user_page.html', {
        'user': page_user,
        'post_list': post_list,
        'post_list_count': post_list_count,
        'is_follow': is_follow,
        'follower_count': follower,
        'following_count': following,

    })


def recent_feed(request):
    timesince = timezone.now() - timedelta(days=7)
    post_list = Post.objects.all()\
        .filter(author=request.user)\
        .filter(created_at__gte=timesince)
    return render(request, 'instagram/recent_feed.html', {
        'post_list': post_list,
        'like_list': request.user.like_post_set.all()[:5],
    })


def look_user(request):
    if request.method == "POST":
        f_name = request.POST.get('q', '')
        f_user = User.objects.all().filter(username=f_name)
        return render(request, 'instagram/look_user.html', {
            'f_user': f_user,
            'f_name': f_name,
        })
    else:
        return render(request, 'instagram/look_user.html')


@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.like_user_set.add(request.user)
    messages.success(request, f'{post}를 좋아합니다.')
    redirect_url = request.META.get("HTTP_REFERER", 'root')
    return redirect(redirect_url)


@login_required
def post_dislike(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # TODO
    post.like_user_set.remove(request.user)
    messages.success(request, f'{post}의 좋아요를 취소합니다.')
    redirect_url = request.META.get("HTTP_REFERER", 'root')
    return redirect(redirect_url)


def post_reply(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        messages.success(request, "댓글이 성공적으로 등록되었습니다.")
        return redirect(post)
    else:
        form = CommentForm
        return render(request, 'instagram/post_reply.html', {'form': CommentForm})


# Create your views here.


class PostViewSet(ModelViewSet):

    queryset = Post.objects.all().select_related(
        "author").prefetch_related("tag_set", "like_user_set")
    # 디버그 툴바로, 중복된 쿼리들 확인 후, select_related로 중복된 쿼리를 제거함
    # queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    # permission_classes = [AllowAny]  # FIXME

    # http http:localhost:8000/accounts/signup/ username=tony password=shirth
    # http http:localhost:8000/accounts/token/ username=tony password=shirth -token 발급
    # http http:localhost:8000/api/posts/ "Authorization: JWT %key%"  요청

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        #     # timesince = timezone.now() - timedelta(days=10)
        # qs = qs.filter(created_at__gte = timesince)
        qs = super().get_queryset()
        qs = qs.filter(
            Q(author=self.request.user) |
            Q(author__in=self.request.user.following_set.all())
        )
        return qs

    # API/ 토큰으로 인증이 되어 요청이 온 경우
# //        serializer.save(author=self.request.user)
    # return super().perform_create(serializer)
    def perform_create(self, serializer):
        author = self.request.user
        serializer.save(author=author)
        return super().perform_create(serializer)

# request.user가 들어가기 위해선 serializers에서 author 필드를 빼주어야한다.
# http POST http://localhost:8000/api/posts/ caption="second message" "Authorization:JWT %key%"
# http POST http://localhost:8000/api/posts/ caption="첫번째 테스트" "Authorization:JWT  %key%"

    @action(detail=True, methods=["POST"])
    def like(self, request, pk):
        post = self.get_object()
        post.like_user_set.add(self.request.user)
        return Response(status.HTTP_204_NO_CONTENT)
# test

    @like.mapping.delete
    def unlike(self, request, pk):
        post = self.get_object()
        post.like_user_set.remove(self.request.user)
        return Response(status.HTTP_204_NO_CONTENT)

# http POST http://localhost:8000/api/posts/3/like/ "Authorization: JWT %key%"


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(post__id=self.kwargs['post_id'])
        return qs

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        author = self.request.user
        serializer.save(author=author, post=post)
        return super().perform_create(serializer)

# http POST http://localhost:8000/api/posts/1/comment/ message="comment" "Authorization:JWT %key%"

