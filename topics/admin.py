from django.contrib import admin

from .models import GeneralTopic, UserTopic, BookReference, WebsiteReference, CourseReference

# Register your models here.

admin.site.register(GeneralTopic)
admin.site.register(UserTopic)
admin.site.register(BookReference)
admin.site.register(WebsiteReference)
admin.site.register(CourseReference)