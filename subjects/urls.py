from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.subjectsDisplay, name='subjects_display'),
    url(r'^add/', views.subjectAdd, name='subjects_add'),
    url(r'^delete/', views.subjectDelete, name='subjects_delete'),
    url(r'^details/', views.subjectsDetail, name='subjects_detail'),
    url(r'^add-reference/', views.subjectsReferenceAdd, name='subjects_reference_add'),
]