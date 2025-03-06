# flowers/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'address')  # Добавьте поля, если хотите их редактировать при регистрации

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Опционально: настройте виджет или метки полей
        self.fields['username'].widget.attrs.update({'placeholder': 'Введите имя пользователя'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Введите email'})