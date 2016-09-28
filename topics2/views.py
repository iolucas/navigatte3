from django.shortcuts import render
from django.http import HttpResponse

from navigatte import wikipedia_api

# Create your views here.


def displayTopic(request, topicurl):

    pageData = wikipedia_api.getPageAbstractLinks(topicurl)
    print(pageData)

    returnLinks = ""

    for link in pageData['abstractLinks']:
        returnLinks += link['title'] + "<br>"
    

    return HttpResponse(returnLinks)
    #return render(request, "topic_page.html")         
