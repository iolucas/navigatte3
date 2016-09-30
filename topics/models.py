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




#Abstract class to store common fields
class MapsCommonFields(models.Model):
    createdIn = models.DateTimeField(auto_now_add=True)
    createdBy = models.ForeignKey(User)
    lastModified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


#Class to store wikipedia articles references
class WikiArticle(MapsCommonFields):

    title = models.CharField(max_length=200)
    #short_description = models.TextField(default="")
    pageId = models.BigIntegerField(unique=True)
    language = models.CharField(max_length=10)

    titleUrl = models.CharField(max_length=200, default="")

    #Field to store abstract urls for this wiki article
    abstractUrls = models.ManyToManyField('WikiUrl')

    def __str__(self):
        return self.title

#Class to store redirection urls of wikipedia articles
class WikiUrl(MapsCommonFields):
    urlPath = models.CharField(max_length=200)
    language = models.CharField(max_length=10)
    pointsTo = models.ForeignKey(WikiArticle, null=True)

    numberOfBacklinks = models.IntegerField(default=-1)

    #Flag to be set if the wikiurl does not exists
    doesNotExists = models.BooleanField(default=False)

    class Meta:
        unique_together = ('urlPath', 'language')

    def __str__(self):
        return self.urlPath + "-" + self.language


#Class to store user set wikiarticle data (such its pre reqs)
class UserWikiArticle(MapsCommonFields):
    #Field to store reference to the wiki article
    wikiArticle = models.ForeignKey(WikiArticle)
    #Field to store the pre requisites articles for this user article
    preReqArticles = models.ManyToManyField(WikiArticle, related_name='prereqs')

    #Flag to be set when the user delete this field
    deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('createdBy', 'wikiArticle')

    def __str__(self):
        return self.wikiArticle.title


