#!/usr/bin/env python
"""
Скрипт для настройки базы данных
Выполните следующие команды в терминале:

1. python manage.py makemigrations
2. python manage.py migrate
3. python manage.py createsuperuser (опционально)
"""

import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User
from app.models import Profile


def setup_database():
    """Настройка базы данных"""

    print("🔧 Создание миграций...")
    execute_from_command_line(['manage.py', 'makemigrations'])

    print("🔧 Применение миграций...")
    execute_from_command_line(['manage.py', 'migrate'])

    print("🔧 Создание профилей для существующих пользователей...")
    # Создаем профили для всех пользователей, у которых их нет
    users_without_profile = User.objects.filter(profile__isnull=True)
    for user in users_without_profile:
        Profile.objects.create(user=user)
        print(f"✅ Создан профиль для пользователя: {user.username}")

    print("✅ База данных настроена успешно!")
    print("\n📝 Для создания суперпользователя выполните:")
    print("python manage.py createsuperuser")


if __name__ == '__main__':
    setup_database()
