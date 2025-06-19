from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.conf import settings
from accounts.models import Profile, Game, Purchase, CommunityPost, PaymentMethod, Transaction
from accounts.forms import CommunityPostForm
import os
import random
from django.http import JsonResponse
from datetime import datetime, timedelta


def login_view(request):
    """Отображение страницы входа и обработка аутентификации"""

    # Если пользователь уже авторизован, перенаправляем на дашборд
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, 'Заполните все поля')
            return render(request, 'index.html')

        # Безопасная проверка существования пользователя
        try:
            # Попытка найти пользователя по email
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.first_name or user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Неверный email или пароль')
        except Exception as e:
            # Обработка ошибок базы данных
            messages.error(request, 'Произошла ошибка при входе. Попробуйте позже.')
            print(f"Ошибка аутентификации: {str(e)}")

    return render(request, 'index.html')


def register_view(request):
    """Отображение страницы регистрации и создание нового пользователя"""

    # Если пользователь уже авторизован, перенаправляем на дашборд
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        terms_accepted = request.POST.get('terms')

        # Валидация
        if not all([first_name, last_name, email, password, confirm_password]):
            messages.error(request, 'Заполните все обязательные поля')
            return render(request, 'reg.html')

        if password != confirm_password:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'reg.html')

        if not terms_accepted:
            messages.error(request, 'Необходимо согласиться с условиями использования')
            return render(request, 'reg.html')

        try:
            # Проверка существования пользователя
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Пользователь с таким email уже существует')
                return render(request, 'reg.html')

            # Создание нового пользователя
            user = User.objects.create_user(
                username=email,  # Используем email как username
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Автоматический вход после регистрации
            login(request, user)

            messages.success(request, f'Аккаунт для {first_name} {last_name} успешно создан!')
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f'Ошибка при создании аккаунта: {str(e)}')
            return render(request, 'reg.html')

    return render(request, 'reg.html')


@login_required(login_url='login')
def dashboard_view(request):
    """Отображение дашборда с фильтрацией игр по категориям"""
    user = request.user

    # Получаем параметр фильтрации из GET-запроса
    category = request.GET.get('category', 'all')

    # Получаем все игры (или фильтруем по категории)
    if category == 'all':
        games = Game.objects.all()
    else:
        games = Game.objects.filter(genre__iexact=category)

    # Убеждаемся, что у пользователя есть профиль
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)

    # Формируем инициалы для аватара
    if user.first_name and user.last_name:
        initials = user.first_name[0].upper() + user.last_name[0].upper()
        full_name = f"{user.first_name} {user.last_name}"
    else:
        initials = user.username[0].upper() + (user.username[1].upper() if len(user.username) > 1 else 'U')
        full_name = user.username

    # Подготавливаем данные игр для шаблона
    games_data = []
    for game in games:
        games_data.append({
            'id': game.id,
            'title': game.title,
            'price': game.price,
            'genre': game.genre,
            'icon': game.icon,
            'developer': game.developer
        })

    context = {
        'user': user,
        'user_name': user.first_name or user.username,
        'initials': initials,
        'full_name': full_name,
        'display_email': user.email or 'Не указан',
        'games': games_data,
        'current_category': category
    }
    return render(request, 'dashboard.html', context)

def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('login')


@login_required(login_url='login')
def support_view(request):
    """Отображение страницы поддержки и обработка запросов"""
    user = request.user

    # Убеждаемся, что у пользователя есть профиль
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)

    if request.method == 'POST':
        # Обработка формы обратной связи
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not all([name, email, subject, message]):
            messages.error(request, 'Заполните все обязательные поля')
            return redirect('support')

        try:
            # Здесь должна быть логика отправки сообщения в поддержку
            # Например, сохранение в базу данных или отправка email

            # Для примера просто логируем
            print(f"Новый запрос в поддержку от {name} ({email}): {subject}\n{message}")

            messages.success(request, 'Ваш запрос отправлен! Мы ответим вам в ближайшее время.')
            return redirect('support')

        except Exception as e:
            messages.error(request, f'Произошла ошибка при отправке запроса: {str(e)}')
            return redirect('support')

    # Формируем инициалы для аватара
    if user.first_name and user.last_name:
        initials = user.first_name[0].upper() + user.last_name[0].upper()
        full_name = f"{user.first_name} {user.last_name}"
    else:
        initials = user.username[0].upper() + (user.username[1].upper() if len(user.username) > 1 else 'U')
        full_name = user.username

    # FAQ данные (можно вынести в базу данных)
    faqs = [
        {
            'question': 'Как восстановить доступ к аккаунту?',
            'answer': 'Если вы забыли пароль, перейдите на страницу входа и нажмите "Забыли пароль?". '
                      'Вам на почту придет ссылка для восстановления. '
                      'Если у вас нет доступа к почте, обратитесь в поддержку с подтверждением владения аккаунтом.'
        },
        {
            'question': 'Как вернуть средства за игру?',
            'answer': 'Возврат средств возможен в течение 14 дней после покупки, если вы провели в игре менее 2 часов. '
                      'Для запроса возврата перейдите в раздел "Мои покупки" в профиле и выберите соответствующую опцию.'
        },
        {
            'question': 'Игра не запускается, что делать?',
            'answer': '1. Проверьте системные требования игры\n'
                      '2. Обновите драйвера видеокарты\n'
                      '3. Попробуйте запустить игру от имени администратора\n'
                      '4. Проверьте целостность файлов игры через клиент GameStore\n'
                      '5. Если проблема сохраняется, обратитесь в поддержку'
        },
        {
            'question': 'Как активировать ключ игры?',
            'answer': 'Для активации ключа:\n'
                      '1. Откройте клиент GameStore\n'
                      '2. Перейдите в раздел "Активировать ключ" в меню\n'
                      '3. Введите 25-значный код\n'
                      '4. Нажмите "Активировать"\n\n'
                      'Игра появится в вашей библиотеке после успешной активации.'
        }
    ]

    context = {
        'user': user,
        'initials': initials,
        'full_name': full_name,
        'display_email': user.email or 'Не указан',
        'faqs': faqs,
        'support_email': 'support@gamestore.com',
        'support_phone': '+7 (800) 123-45-67',
        'telegram_link': 'https://t.me/gamestore_support',
        'page_title': 'Служба поддержки GameStore',
        'page_subtitle': 'Мы всегда готовы помочь вам с любыми вопросами и проблемами'
    }

    return render(request, 'support.html', context)
@login_required
def community_view(request):
    """Страница сообщества с постами и профилями"""
    user = request.user

    # Получаем все посты из сообщества
    posts = CommunityPost.objects.all().order_by('-created_at')

    # Формируем данные для вашего профиля
    developer_profile = {
        'username': 'mikel',
        'email': 'mikhail52gr@gmail.com',
        'role': 'Разработчик GameStore',
        'bio': 'Создатель и главный разработчик этого игрового магазина. Специализируюсь на Python/Django и веб-разработке.',
        'join_date': '2023-01-15',
        'posts_count': CommunityPost.objects.filter(author__username='mikel').count(),
        'avatar': '/static/images/developer_avatar.png'  # Добавьте изображение в static
    }

    context = {
        'user': user,
        'developer': developer_profile,
        'posts': posts,
        'page_title': 'Сообщество GameStore',
        'page_subtitle': 'Обсуждайте игры, делитесь решениями и находите единомышленников'
    }
    return render(request, 'community.html', context)


@login_required
def create_post_view(request):
    """Создание нового поста в сообществе"""
    if request.method == 'POST':
        form = CommunityPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост успешно опубликован!')
            return redirect('community')
    else:
        form = CommunityPostForm()

    return render(request, 'create_post.html', {'form': form})
@login_required
def like_post_view(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(CommunityPost, id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes.count()
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def balance_view(request):
    try:
        # Получаем профиль пользователя
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Если профиль не существует, создаем его
        profile = Profile.objects.create(user=request.user, balance=0.00)

    # Получаем платежные методы и транзакции
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[
                   :10]  # Исправлено на created_at

    context = {
        'balance': profile.balance,
        'payment_methods': payment_methods,
        'transactions': transactions
    }
    return render(request, 'balance.html', context)
@login_required(login_url='login')
def library(request):
    """Отображение страницы библиотеки с фильтрацией игр"""
    user = request.user

    # Получаем параметры фильтрации из GET-запроса
    genre_filter = request.GET.get('genre', 'all')
    status_filter = request.GET.get('status', 'all')

    # Убеждаемся, что у пользователя есть профиль
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)

    # Получаем все покупки пользователя
    user_purchases = Purchase.objects.filter(user=user).select_related('game')

    # Подготавливаем данные игр для шаблона
    games_data = []
    for purchase in user_purchases:
        game = purchase.game
        # Преобразуем release_date в date, если это datetime
        release_date = game.release_date.date() if hasattr(game.release_date, 'date') else game.release_date
        today = datetime.now().date()

        # Определяем статус игры
        days_since_release = (today - release_date).days
        status = 'new' if days_since_release < 30 else 'regular'
        status = 'free' if game.price == 0 else status

        games_data.append({
            'id': game.id,
            'title': game.title,
            'price': game.price,
            'genre': game.genre,
            'icon': game.icon,
            'purchase_date': purchase.date.strftime('%d.%m.%Y'),
            'status': status,
            'is_new': days_since_release < 30,
            'is_free': game.price == 0,
            'is_premium': game.price >= 2000,
            'is_on_sale': game.price < 1000  # Пример условия для скидки
        })

    # Применяем фильтры
    filtered_games = []
    for game in games_data:
        genre_match = genre_filter == 'all' or game['genre'].lower() == genre_filter.lower()
        status_match = status_filter == 'all' or (
                (status_filter == 'new' and game['is_new']) or
                (status_filter == 'sale' and game['is_on_sale']) or
                (status_filter == 'free' and game['is_free']) or
                (status_filter == 'premium' and game['is_premium'])
        )

        if genre_match and status_match:
            filtered_games.append(game)

    # Формируем инициалы для аватара
    if user.first_name and user.last_name:
        initials = user.first_name[0].upper() + user.last_name[0].upper()
        full_name = f"{user.first_name} {user.last_name}"
    else:
        initials = user.username[0].upper() + (user.username[1].upper() if len(user.username) > 1 else 'U')
        full_name = user.username

    context = {
        'user': user,
        'initials': initials,
        'full_name': full_name,
        'display_email': user.email or 'Не указан',
        'games': filtered_games,
        'total_games': len(filtered_games),
        'total_spent': sum(game['price'] for game in filtered_games),
        'page_title': 'Библиотека игр',
        'page_subtitle': 'Откройте для себя лучшие игры этого месяца',
        'current_genre': genre_filter,
        'current_status': status_filter
    }

    return render(request, 'library.html', context)
@login_required(login_url='login')
def settings_view(request):
    """Отображение страницы настроек аккаунта"""

    # Убеждаемся, что у пользователя есть профиль
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        # Обработка загрузки аватара
        if action == 'change_avatar' and request.FILES.get('avatar'):
            try:
                # Если у пользователя уже есть аватар, удаляем его
                if request.user.profile.avatar:
                    if os.path.isfile(request.user.profile.avatar.path):
                        os.remove(request.user.profile.avatar.path)

                # Сохраняем новый аватар
                request.user.profile.avatar = request.FILES['avatar']
                request.user.profile.save()

                messages.success(request, 'Фото профиля успешно обновлено!')
            except Exception as e:
                messages.error(request, f'Ошибка при загрузке фото: {str(e)}')

        # Обработка удаления аватара
        elif action == 'delete_avatar':
            try:
                if request.user.profile.avatar:
                    if os.path.isfile(request.user.profile.avatar.path):
                        os.remove(request.user.profile.avatar.path)
                    request.user.profile.avatar = None
                    request.user.profile.save()

                messages.success(request, 'Фото профиля удалено!')
            except Exception as e:
                messages.error(request, f'Ошибка при удалении фото: {str(e)}')

        # Обработка обновления профиля
        else:
            first_name = request.POST.get('firstName')
            last_name = request.POST.get('lastName')
            email = request.POST.get('email')

            # Валидация данных
            if not first_name or not last_name:
                messages.error(request, 'Имя и фамилия обязательны для заполнения')
                return redirect('settings')

            # Проверка уникальности email (если изменился)
            if email and email != request.user.email:
                if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                    messages.error(request, 'Пользователь с таким email уже существует')
                    return redirect('settings')

            try:
                # Обновление данных пользователя
                request.user.first_name = first_name
                request.user.last_name = last_name
                if email:
                    request.user.email = email
                request.user.save()

                messages.success(request, 'Профиль успешно обновлен!')
            except Exception as e:
                messages.error(request, f'Ошибка при обновлении профиля: {str(e)}')

        return redirect('settings')

    # Получаем данные текущего пользователя
    user = request.user

    # Формируем инициалы для аватара
    if user.first_name and user.last_name:
        initials = user.first_name[0].upper() + user.last_name[0].upper()
        full_name = f"{user.first_name} {user.last_name}"
    else:
        initials = user.username[0].upper() + (user.username[1].upper() if len(user.username) > 1 else 'U')
        full_name = user.username

    context = {
        'user': user,
        'initials': initials,
        'full_name': full_name,
        'display_email': user.email or 'Не указан',
    }
    return render(request, 'settings.html', context)

@login_required
def payment_methods_view(request):
    if request.method == 'POST':
        # Обработка добавления нового метода оплаты
        pass

    methods = PaymentMethod.objects.filter(user=request.user)
    return render(request, 'payment_methods.html', {'payment_methods': methods})
@login_required(login_url='login')
def purchases_view(request):
    """Отображение страницы покупок пользователя"""

    # Убеждаемся, что у пользователя есть профиль
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    # Получаем покупки пользователя
    user_purchases = Purchase.objects.filter(user=request.user).select_related('game')

    # Если у пользователя нет покупок, создаем тестовые данные (для демонстрации)
    if not user_purchases.exists() and settings.DEBUG:
        # Создаем тестовые игры, если их нет
        if not Game.objects.exists():
            games = [
                {
                    'title': 'Cyber Adventure',
                    'description': 'Захватывающее приключение в мире будущего',
                    'price': 1299,
                    'genre': 'Экшен',
                    'developer': 'Future Games',
                    'release_date': datetime.now() - timedelta(days=30),
                    'icon': '🎯'
                },
                {
                    'title': 'Fantasy Quest',
                    'description': 'Эпическое фэнтези-приключение',
                    'price': 899,
                    'genre': 'RPG',
                    'developer': 'Epic Studios',
                    'release_date': datetime.now() - timedelta(days=60),
                    'icon': '⚔️'
                },
                {
                    'title': 'Speed Racing',
                    'description': 'Гоночный симулятор нового поколения',
                    'price': 1599,
                    'genre': 'Гонки',
                    'developer': 'Fast Lane Games',
                    'release_date': datetime.now() - timedelta(days=15),
                    'icon': '🏎️'
                },
                {
                    'title': 'F1',
                    'description': 'Гонки на Formula 1',
                    'price': 2199,
                    'genre': 'Гонки',
                    'developer': 'Epic game',
                    'release_date': datetime.now() - timedelta(days=7),
                    'icon': '🏎️'
                },
                {
                    'title': 'Euro Truck Semulator 2 ',
                    'description': 'Доставляйте грузы на полупрецепе по европе',
                    'price': 3199,
                    'genre': 'Симулятор',
                    'developer': 'Unreal Games',
                    'release_date': datetime.now() - timedelta(days=17),
                    'icon': '🚀'
                },
                {
                    'title': 'Genshin Impact',
                    'description': 'Исследуйте бескрайние просторы космоса',
                    'price': 1199,
                    'genre': 'RPG',
                    'developer': 'Stellar Games',
                    'release_date': datetime.now() - timedelta(days=27),
                    'icon': '#'
                }

            ]

            for game_data in games:
                # Проверяем, существует ли уже такая игра
                if not Game.objects.filter(title=game_data['title']).exists():
                    Game.objects.create(**game_data)
                    print(f"Created game: {game_data['title']}")

        # Создаем тестовые покупки
        games = Game.objects.all()
        for game in games[:10]:  # Добавляем только 2 игры для демонстрации
            Purchase.objects.create(
                user=request.user,
                game=game,
                price=game.price,
                date=datetime.now() - timedelta(days=random.randint(1, 10))
            )

        # Обновляем список покупок
        user_purchases = Purchase.objects.filter(user=request.user).select_related('game')

    # Подготавливаем данные для шаблона
    purchases_data = []
    for purchase in user_purchases:
        purchases_data.append({
            'id': purchase.id,
            'title': purchase.game.title,
            'genre': purchase.game.genre,
            'developer': purchase.game.developer,
            'price': purchase.price,
            'date': purchase.date.strftime('%d.%m.%Y %H:%M'),
            'icon': purchase.game.icon
        })

    # Формируем инициалы для аватара
    user = request.user
    if user.first_name and user.last_name:
        initials = user.first_name[0].upper() + user.last_name[0].upper()
        full_name = f"{user.first_name} {user.last_name}"
    else:
        initials = user.username[0].upper() + (user.username[1].upper() if len(user.username) > 1 else 'U')
        full_name = user.username

    context = {
        'user': user,
        'initials': initials,
        'full_name': full_name,
        'display_email': user.email or 'Не указан',
        'purchases': purchases_data
    }

    return render(request, 'purchases.html', context)
