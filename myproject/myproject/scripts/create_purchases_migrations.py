#!/usr/bin/env python
"""
Скрипт для создания миграций для моделей Game и Purchase
"""

import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.core.management import execute_from_command_line


def create_migrations():
    """Создание миграций для моделей Game и Purchase"""

    print("🔧 Создание миграций для моделей Game и Purchase...")
    execute_from_command_line(['manage.py', 'makemigrations', 'accounts'])

    print("🔧 Применение миграций...")
    execute_from_command_line(['manage.py', 'migrate'])

    print("✅ Миграции успешно созданы и применены!")


if __name__ == '__main__':
    create_migrations()
