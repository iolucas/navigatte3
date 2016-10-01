from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.displayUserArticles, name='display_user_topics'),
    
    #url(r'^display-user-topics/', views.displayUserTopics, name='display_user_topics'),
    #Start using topic url title as link
    #url(r'^$', views.displayUserTopicsByName, name='display_user_topics'),
    #subjects/(?P<userpage>\w+)/
    
    url(r'^add-new-user-topic/', views.addNewUserArticle, name='add_new_user_topic'),
    #url(r'^user-topic-details/', views.userArticleDetails, name='user_topic_details'),
    url(r'^delete-user-topic/', views.deleteUserArticle, name='delete_user_topic'),
    #url(r'^add-user-topic-reference/', views.addUserTopicReference, name='add_user_topic_reference'),
    #url(r'^delete-user-topic-reference/', views.deleteUserTopicReference, name='delete_user_topic_reference'),


    url(r'^map/$', views.displayUserMap, name='displayUserMap'),

    url(r'^(?P<articleId>\w+)/$', views.displayUserArticlesDetails, name='displayUserArticlesDetails'),
    url(r'^(?P<articleId>\w+)/search/$', views.displayUserArticlesSearch, name='displayUserArticlesSearch'),

    url(r'^(?P<articleId>\w+)/addUserArticlePreRequisite$', views.addUserArticlePreRequisite, name='addUserArticlePreRequisite'),
    url(r'^(?P<articleId>\w+)/deleteUserArticlePreRequisite$', views.deleteUserArticlePreRequisite, name='deleteUserArticlePreRequisite'),
]