from django import template

register = template.Library()

@register.filter
def is_like_user(post, user):
    return post.is_like_user(user)


# 모델 포스트 is_lie_user호출 
