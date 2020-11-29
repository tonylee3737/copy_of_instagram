# from accounts.models import User 이거 대신 셋팅스로 정의하는 것이 훨씬 용이하다.
import re
from django.conf import settings
from django.db import models
from django.urls import reverse
# from instagram.models import Post


class BaseModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
#  어떤 유저가 작성한 목록을 가져오기
# -> post.objects.filter(author = user)
# -> user.post_set.all()  -> user.my_post_set.all()   // 모델명_set으로 자동생성 그러나 ManyToMany필드에서 Foreginkey충돌, related_name을 수정 또는 related_name = "+"를 하면 포기하기.


class Post(BaseModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='my_post_set', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='instagram/post/%Y/%M')
    caption = models.CharField(max_length=500, blank=True)
    tag_set = models.ManyToManyField('Tag', blank=True)
    location = models.CharField(max_length=100, blank=True)
    like_user_set = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='like_post_set', blank=True)

    def __str__(self):
        return self.caption

    def extract_caption(self):
        tag_name = re.findall(r"#([a-zA-Z\dㄱ-힣]+)", self.caption)
        #\d means [0-9]                                              
        tag_list = []
        for tag in tag_name:
            tag, _ = Tag.objects.get_or_create(name=tag)
            # get_or_create is a tuple, it returns obj, boolean('created')
            tag_list.append(tag)
        return tag_list

    def get_absolute_url(self):
        return reverse('instagram:post_detail', args=[self.pk])

#  이미 유저가 좋아요를 누른 상태를 확인하는 매소드
    def is_like_user(self, user):
        return self.like_user_set.filter(pk=user.pk).exists()

    class Meta:
        ordering = ['-id']


class Comment(BaseModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    message = models.TextField(max_length=1000, blank=False)

    class Meta:
        ordering = ['-id']


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# class LikeUser(models.Model):
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL,
#                              on_delete=models.CASCADE)                    <- 두번째 방법 좋아요 누르는 방법.. TODO
