from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.homeIndex, name='home_index'),
]