"""navigatte URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.nvgttIndex),

    #General options
    url(r'^admin/interface/', admin.site.urls),
    url(r'^register/', include('register.urls')),
    url(r'^login/', include('login.urls')),
    
    url(r'^home/', include('home.urls')),

    #url(r'^topic/', include('topics2.urls')),

    #url(r'^maps/', include('maps.urls')),

    #User related options
    #url(r'^(?P<userpage>\w+)/', include('user.urls')),
    url(r'^subjects/(?P<userpage>\w+)/', include('subjects.urls')),
    url(r'^(?P<userpage>\w+)/', include('topics.urls')),
]
