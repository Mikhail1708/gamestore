from django import forms
from .models import CommunityPost  # импорт модели из текущего приложения

class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок поста'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Содержание поста...'
            }),
        }
        labels = {
            'title': 'Заголовок',
            'category': 'Категория',
            'content': 'Содержание'
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 10:
            raise forms.ValidationError("Заголовок должен содержать минимум 10 символов")
        return title