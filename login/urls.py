from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.login, name='login_index'),
    url(r'^logout/', views.logout, name='logout_index'),
]