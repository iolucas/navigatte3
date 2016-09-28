from django.db import models

from django.contrib.auth.models import User

# Create your models here.

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
    pageid = models.BigIntegerField(unique=True)
    language = models.CharField(max_length=10)

    #Field to store abstract urls for this wiki article
    abstractUrls = models.ManyToManyField('WikiUrl', blank=True)

    def __str__(self):
        return self.title

#Class to store redirection urls of wikipedia articles
class WikiUrl(MapsCommonFields):
    urlPath = models.CharField(max_length=200)
    language = models.CharField(max_length=10)
    pointsTo = models.ForeignKey(WikiArticle)

    class Meta:
        unique_together = ('urlPath', 'language')

    def __str__(self):
        return self.urlPath + "-" + self.language


#Class to store user set wikiarticle data (such its pre reqs)
class UserWikiArticle(MapsCommonFields):
    #Field to store reference to the wiki article
    wikiArticle = models.ForeignKey(WikiArticle)
    #Field to store the pre requisites articles for this user article
    preReqArticles = models.ManyToManyField(WikiArticle, blank=True, related_name='prereqs')

    #Flag to be set when the user delete this field
    deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('createdBy', 'wikiArticle')

    def __str__(self):
        return self.wikiArticle.title
