from django.db import models

from topics.models import GeneralTopic

# Create your models here.

#User topic that stores user topics
class AbstractLinks(models.Model):
    generalTopic = models.OneToOneField(GeneralTopic)

    #Abstract Links
    #links = models.ManyToManyField(GeneralTopic, blank=True, related_name='abstractLinks')
    #Abstract links that does not have a reverse link to this object
    nonReverseLinks = models.ManyToManyField(GeneralTopic, blank=True, related_name='nonReverseAbLinks')

    def __str__(self):
        return self.generalTopic.title