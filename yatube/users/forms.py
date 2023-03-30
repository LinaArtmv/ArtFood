from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class ChangePassword(forms.Form):
    old_password = forms.CharField(label='Старый пароль')
    new_password = forms.CharField(label='Новый пароль')
    repeat_new_password = forms.CharField(label='Новый пароль(повторно)')


password = ChangePassword()
