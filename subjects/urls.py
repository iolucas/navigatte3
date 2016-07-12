from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.subjectsOwnerDisplay, name='subjects_owner_display'),
    url(r'^add/', views.subjectAdd, name='subjects_add'),
    url(r'^details/', views.subjectsDetail, name='subjects_detail'),
]