from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<topicurl>\w+)/', views.displayTopic, name='display_topic'),
]