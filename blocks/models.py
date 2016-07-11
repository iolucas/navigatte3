from django.db import models

# Create your models here.

class Block(models.Model):
    name = models.CharField(max_length=200)
    #block_description = models.TextField()

    #Blocks that are recommended pre-requisites for this block
    parents = models.ManyToManyField("Block", blank=True)

    #Learn references
    books = models.ManyToManyField("Book", blank=True)
    websites = models.ManyToManyField("Website", blank=True)
    courses = models.ManyToManyField("Course", blank=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    name = models.CharField(max_length=200) 

    def __str__(self):
        return self.name

class Website(models.Model):
    name = models.CharField(max_length=200) 

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=200) 

    def __str__(self):
        return self.name