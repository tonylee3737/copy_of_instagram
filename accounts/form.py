from django.forms import ModelForm
from accounts.models import User
from django.contrib.auth.forms import (
    UserCreationForm, PasswordChangeForm as AuthPasswordChangeForm)
from django import forms


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwagrs):
        super().__init__(*args, **kwagrs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs:
            raise forms.ValidationError("이미 등록된 이메일 입니다.")
        else:
            return email

    # def clean_first_name(self):
    #     first_name = self.cleaned_data.get('first_name')
    #     qs = User.objects.filter(first_name=first_name)
    #     if qs:
    #         raise forms.ValidationError("이미 등록된 이름입니다.")
    #     else:
    #         return first_name


class EditForm(ModelForm):
    class Meta:
        model = User
        fields = ['user_photo', 'username', 'gender', 'first_name',
                  'last_name', 'phone_number', 'email']


class PasswordChangeForm(AuthPasswordChangeForm):
    #    form을 그대로 사용하기 때문에 Meta를 구현할 필요가 없다.
    def clean_new_password2(self):
        old_password = self.cleaned_data.get('old_password')
        password2 = self.cleaned_data.get('new_password2')
        if old_password and password2:
            if old_password == password2:
                raise forms.ValidationError(" 전과 동일한 비밀번호를 입력하셨습니다.")
# 리턴 값이 있는 것이 본 폼의 구현이기 때문에 항상 리턴을 준다/ 리턴값은 변경된 패스워드
        return password2
