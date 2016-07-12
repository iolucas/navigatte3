from django.contrib import admin

# Register your models here.

from .models import Subject, Book, Course, Website

admin.site.register(Subject)
admin.site.register(Book)
admin.site.register(Course)
admin.site.register(Website)
