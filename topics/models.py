from django.db import models

from django.contrib.auth.models import User

# Create your models here.

#Abstract class to inherit all models of the system
class nvgttModel(models.Model):
    createdIn = models.DateTimeField(auto_now_add=True)
    createdBy = models.ForeignKey(User)
    lastModified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True




#General topic that handles topics to be used by the users
class GeneralTopic(models.Model):

    title = models.CharField(max_length=200)
    #short_description = models.TextField(default="")
    #url = models.URLField(unique=True)
    pageid = models.BigIntegerField(unique=True)
    urlTitle = models.CharField(max_length=200, unique=True)
    #language = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.title


#User topic that stores user topics
class UserTopic(models.Model):
    generalTopic = models.ForeignKey(GeneralTopic)

    deleted = models.BooleanField(default=False)

    #Blocks that are recommended pre-requisites for this block
    parents = models.ManyToManyField("UserTopic", blank=True)

    #Learn references
    books = models.ManyToManyField("BookReference", blank=True)
    websites = models.ManyToManyField("WebsiteReference", blank=True)
    courses = models.ManyToManyField("CourseReference", blank=True)

    #user that owns this block
    owner = models.ForeignKey(User)

    def __str__(self):
        return self.generalTopic.title

#Abstract class to inherit all Subject references
class UserTopicReference(models.Model):
    name = models.CharField(max_length=200)
    short_description = models.CharField(max_length=200, blank=True)
    long_description = models.CharField(max_length=1000, blank=True)  

    #deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class BookReference(UserTopicReference):
    author = models.CharField(max_length=100, blank=True)
    

class WebsiteReference(UserTopicReference):
    address = models.URLField(max_length=1000, unique=True)


class CourseReference(UserTopicReference):
    country = models.CharField(max_length=50, blank=True) 


