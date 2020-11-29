from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()
# 회원가입 요청 시, 응답할 API
class SignupSerializer(ModelSerializer):
    password = serializers.CharField(write_only = True)
# 비밀번호는 셋으로 암호화한다. 
    def create(self, validated_data):
        user = User.objects.create(username = validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        return user         
# 보여질 필드 나열하기 
    class Meta:
        model = User
        fields = ['pk','username','password']

# 추천 유저들 API. 
class SuggestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # 이름만 보여주도록 한다. 
        fields = ['username']


