from django.shortcuts import render

from django.http import HttpResponse

from navigatte import wikipedia_api

from topics.models import GeneralTopic

import re

#implement boxes, parent references and projections
#check about diferente names for links and title
#Message to register to get more detailed info back knowledges, and possible knowledges

def homeIndex(request):

    lang = "en"
    if 'lang' in request.GET and request.GET['lang']:
        lang = request.GET['lang']

    if 'search' in request.GET and request.GET['search']:
        searchResults = wikipedia_api.search(request.GET['search'], lang)
        return render(request, "home.html", {
            'search': True,
            'searchResults': searchResults
        })

    if 'query' in request.GET and request.GET['query']:
        
        queryResult = wikipedia_api.getPageAbstractLinks(request.GET['query'], lang)

        #If we got a valid page id, try to add the page to the general topics
        if queryResult['pageId'] != -1:
            #Try to get topic, if not found, create a new
            try: 
                topicReference = GeneralTopic.objects.get(pageid=queryResult['pageId'])
            except GeneralTopic.DoesNotExist:
                topicReference = GeneralTopic(
                    title=queryResult['article'], 
                    pageid=queryResult['pageId'], 
                    urlTitle=queryResult['articleUrl'])
                topicReference.save()


        return render(request, "home.html", {
            'query': True,
            'article': queryResult['article'],
            'abstractLinks': queryResult['abstractLinks']
        })


    return render(request, "home.html")    



    #return render(request, "home.html")

    #result = wikipedia_api.getPageAbstractLinks("Contabilidade", "pt")

    #resultStr = "<br><br>".join(result)

    #return HttpResponse(resultStr)

    #if request.user.is_authenticated():
        #return redirect("display_user_topics", request.user.username)

   # return redirect('login_index')