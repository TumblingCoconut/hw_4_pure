from django.urls import include, path
from . import views

urlpatterns = [
    # HW2
    path('time', views.time_view, name='time'),
    path('sum', views.sum_view, name='sum'),
    path('', views.index, name='home'),
    path('index.html', views.index, name='index.html'),
    path('new.html', views.new, name='new.html'),

    path('createUser', views.create_new, name='create_user'),

]
