from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.homeWelcome, name='home_index'),
]