from django.urls import path
from src.pages import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register_view, name='register'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('diary', views.diary_view, name='diary'),
    path('add', views.add_view, name='add'),
    path('read/<int:entry_id>', views.read_view, name='read'),
    path('edit/<int:entry_id>', views.edit_view, name='edit'),
    path('delete/<int:entry_id>', views.delete_view, name='delete'),
    path('profile', views.profile_view, name='profile')
]