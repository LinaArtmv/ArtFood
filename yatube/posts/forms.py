from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta():
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data.get('text')
        if not data:
            raise forms.ValidationError('Поле должно быть заполненным!')
        return data


class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        fields = ('text',)

    def clean_text(self):
        data = self.cleaned_data.get('text')
        if not data:
            raise forms.ValidationError('Поле должно быть заполненным!')
        return data
