from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns


app_name = 'jb'
urlpatterns = [
    path('', views.index, name='index'),
    path('listen', views.index),
    path('listen/<slug:room_slug>', views.listen, name='listen'),
    path('manage', views.index),
    path('manage/<slug:room_id>', views.manage, name='manage'),
    path('api/<slug:room_slug>', views.CurrentStateView.as_view()),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('contact', views.contact, name='contact')
    ]
