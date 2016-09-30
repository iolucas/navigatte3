from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.displayUserTopics, name='display_user_topics'),
    
    #url(r'^display-user-topics/', views.displayUserTopics, name='display_user_topics'),
    #Start using topic url title as link
    #url(r'^$', views.displayUserTopicsByName, name='display_user_topics'),
    #subjects/(?P<userpage>\w+)/
    
    url(r'^add-new-user-topic/', views.addNewUserTopic, name='add_new_user_topic'),
    url(r'^user-topic-details/', views.userTopicDetails, name='user_topic_details'),
    url(r'^delete-user-topic/', views.deleteUserTopic, name='delete_user_topic'),
    url(r'^add-user-topic-reference/', views.addUserTopicReference, name='add_user_topic_reference'),
    url(r'^delete-user-topic-reference/', views.deleteUserTopicReference, name='delete_user_topic_reference'),

    url(r'^(?P<articleId>\w+)/$', views.displayUserArticlesDetails, name='displayUserArticlesDetails'),
    url(r'^(?P<articleId>\w+)/search/$', views.displayUserArticlesSearch, name='displayUserArticlesSearch'),

    url(r'^(?P<articleId>\w+)/addUserArticlePreRequisite$', views.addUserArticlePreRequisite, name='addUserArticlePreRequisite'),
]