from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.blocksDisplay, name='blocks_index'),
    url(r'^add/', views.blockAdd, name='blocks_add'),
    url(r'^details/', views.blockDetails, name='block_details'),
]