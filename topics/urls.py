from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.displayUserTopics, name='display_user_topics'),
    #url(r'^display-user-topics/', views.displayUserTopics, name='display_user_topics'),
    
    url(r'^add-new-user-topic/', views.addNewUserTopic, name='add_new_user_topic'),
    url(r'^user-topic-details/', views.userTopicDetails, name='user_topic_details'),
    url(r'^delete-user-topic/', views.deleteUserTopic, name='delete_user_topic'),
    url(r'^add-user-topic-reference/', views.addUserTopicReference, name='add_user_topic_reference'),
    url(r'^delete-user-topic-reference/', views.deleteUserTopicReference, name='delete_user_topic_reference'),
]