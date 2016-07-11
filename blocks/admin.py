from django.contrib import admin

# Register your models here.

from .models import Block, Book, Course, Website

admin.site.register(Block)
admin.site.register(Book)
admin.site.register(Course)
admin.site.register(Website)
