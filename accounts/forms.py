from allauth.account.forms import LoginForm
from django import forms
from django.contrib.auth.forms import (UserCreationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm)
from django.contrib.auth.models import User

from accounts.models import Profile
from utils.forms import update_fields_widget


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('username', 'password1', 'password2'), 'form-control')


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', )


class CustomAuthenticationForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('login', 'password'), 'form-control')


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('old_password', 'new_password1', 'new_password2'), 'form-control')


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('email',), 'form-control')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'Пользователя с email: {email} не существует')
        return cleaned_data


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('new_password1', 'new_password2',), 'form-control')



