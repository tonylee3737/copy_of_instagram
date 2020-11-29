from rest_framework import serializers
from instagram.models import Post, Comment
from django.conf import settings
from django.contrib.auth import get_user_model


# class AuthorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = get_user_model()
#         fields = ["id"]


class PostSerializer(serializers.ModelSerializer):
    # author = AuthorSerializer()
    is_like = serializers.SerializerMethodField('is_like_field')

    def is_like_field(self, post):
        if 'request' in self.context:
            user = self.context['request'].user
            return post.like_user_set.filter(pk=user.pk).exists()
        return False

    class Meta:
        model = Post
        fields = ['caption', 'photo', 'is_like']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['message']

