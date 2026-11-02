from django.urls import include, path
from . import views

urlpatterns = [
    # HW2
    path('time', views.time_view, name='time'),
    path('sum', views.sum_view, name='sum'),
    path('new.html', views.new, name='new.html'),
    path('', views.index, name='home'),
    path('index.html', views.index, name='index_html'),
    path('createUser', views.create_new, name='create_user'),

]