from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.userIndex, name='user_index'),
]