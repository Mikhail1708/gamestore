from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from myproject import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('settings/', views.settings_view, name='settings'),
    path('purchases/', views.purchases_view, name='purchases'),
    path('logout/', views.logout_view, name='logout'),
    path('library/', views.library, name='library'),
    path('community/', views.community_view, name='community'),
    path('community/create/', views.create_post_view, name='create_post'),
    path('support/', views.support_view, name='support'),
    path('balance/', views.balance_view, name='balance'),
    path('payment-methods/', views.payment_methods_view, name='payment_methods'),
]

# Добавляем обслуживание медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
