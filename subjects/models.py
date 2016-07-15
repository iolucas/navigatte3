from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class Subject(models.Model):
    name = models.CharField(max_length=200)
    #description = models.TextField()

    deleted = models.BooleanField(default=False)

    #Blocks that are recommended pre-requisites for this block
    parents = models.ManyToManyField("Subject", blank=True)

    #Learn references
    books = models.ManyToManyField("Book", blank=True)
    websites = models.ManyToManyField("Website", blank=True)
    courses = models.ManyToManyField("Course", blank=True)

    #user that owns this block
    owner = models.ForeignKey(User)

    def __str__(self):
        return self.name

#Abstract class to inherit all Subject references
class SubjectReference(models.Model):
    name = models.CharField(max_length=200)
    short_description = models.CharField(max_length=200, blank=True)
    long_description = models.CharField(max_length=1000, blank=True)  

    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Book(SubjectReference):
    author = models.CharField(max_length=100, blank=True)
    

class Website(SubjectReference):
    address = models.CharField(max_length=2000, blank=True)


class Course(SubjectReference):
    country = models.CharField(max_length=50, blank=True) 
