from django.urls import include, path
from . import views

urlpatterns = [
    # HW2
    path('time', views.time_view, name='time'),
    path('sum', views.sum_view, name='sum'),
    path('new', views.new, name='new'),
    path('', views.index, name='home'),
    path('index.html', views.index, name='index_html'),
    path('createUser', views.create_new, name='create_user'),

    path('new_course', views.newCoursePage, name='new_course'),
    path('createCourse/', views.createCourse, name="createCourse"),

    path('new_lecture', views.newLecturePage, name='new_lecture'),
    path('createLecture', views.createLecture, name='createLecture'),
    
    path('new_qr_upload', views.newQRUploadPage, name='new_qr_upload'),
    path('createQRCodeUpload', views.createQRCodeUpload, name='createQRCodeUpload'),

    path("dumpUploads", views.dumpUploads, name="dumpUploads")

]