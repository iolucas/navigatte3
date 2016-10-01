from django.shortcuts import render

from django.http import HttpResponse

from topics import wikipedia_api2 as wikipedia_api

from topics.models import GeneralTopic

from urllib.parse import quote, unquote

from .models import AbstractLinks

from django.contrib.auth.models import User

import re

#implement boxes, parent references and projections
#check about diferente names for links and title
#Message to register to get more detailed info back knowledges, and possible knowledges



def homeWelcome(request):
    #Get all the users
    allUsers = User.objects.all()

    registeredUsers = []

    for regUser in allUsers:
        registeredUsers.append(regUser.username)

    return render(request, "homeWelcome.html", {
        'registeredUsers': registeredUsers    
    })




#create welcome page with users
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
        
        pageUrl = request.GET['query']

        pageReference = getOrCreateGeneralTopic(pageUrl)

        #Try to get the abstract reference
        try:
            abstractLinkReference = AbstractLinks.objects.get(generalTopic=pageReference)

        #If does not exists,
        except AbstractLinks.DoesNotExist:
            # create a new
            abstractLinkReference = AbstractLinks(generalTopic=pageReference)
            abstractLinkReference.save()

            #query the non reverse links of the target page
            nonReverseLinks = wikipedia_api.getAbstractNonReverseLinks(pageUrl, lang)

            #Iterate thru all the links and get their data
            for link in nonReverseLinks:
                linkReference = getOrCreateGeneralTopic(link)
                if linkReference == None:
                    continue
                #Add the non reverse link to its list
                abstractLinkReference.nonReverseLinks.add(linkReference)

            abstractLinkReference.save()

        #Array to store the reverse links
        nonReverseLinks = []
        for link in abstractLinkReference.nonReverseLinks.all():
            nonReverseLinks.append({
                'title': link.title,
                'href': link.urlTitle
            })

            #check the issue of when we request c#
            #probably due to out of memory on bluemix
            #maybe forgot about the non revverse for now

        return render(request, "home.html", {
            'query': True,
            'article': pageReference.title,
            'abstractLinks': nonReverseLinks
        })

    #If no query string is passed, return the home
    return render(request, "home.html")  

        #http://nvgtt-utils.mybluemix.net/wikipedia-nonreverse-links?page=c%2b%2b
        #Ensure the page is in the proper format for comparison with links
        #page = wikipedia_api.normalizeWikiLink(request.GET['query'], lang)

        #queryResult = getAbstractLinks(page, lang)

        #newAbstractLinkReference = False


        
        
        #If does not exists, create a new
        #except AbstractLinks.DoesNotExist:
            #abstractLinkReference = AbstractLinks(generalTopic=queryResult['topicReference'])
            #abstractLinkReference.save()
            #newAbstractLinkReference = True
        
        #must define method that on wikipedia get abstract link, it searchs in the database, if is not there, get from wikipedia and populate on the local db
        #method is useful because of the twice call for reverse link verification

        #Non reverse links array
        #nonReverseLinks = []
        #abstractLinks = queryResult['abstractLinks']

        #for link in abstractLinks:

            #linkQueryResult = getAbstractLinks(link['href'], lang)

            #If the query result is not valid, print it and return none
            #if linkQueryResult == None:
                #continue
"""
            if newAbstractLinkReference:
                #Add this link to the abstract links
                abstractLinkReference.links.add(linkQueryResult['topicReference'])

            if not hrefExistsOn(linkQueryResult['abstractLinks'], page, lang):
                nonReverseLinks.append(link)
                
                if newAbstractLinkReference:
                    #Add link to the non reverse collection
                    abstractLinkReference.nonReverseLinks.add(linkQueryResult['topicReference'])

        return render(request, "home.html", {
            'query': True,
            'article': queryResult['article'],
            'abstractLinks': nonReverseLinks
        })"""


  






def getOrCreateGeneralTopic(urlTitle):
    #Try to get the local reference of the query
    try:
        pageReference = GeneralTopic.objects.get(urlTitle=urlTitle)

    except GeneralTopic.DoesNotExist:

        #If it does not exists, query this page
        queryResult = wikipedia_api.query(urlTitle)
        if queryResult == None:
            return None;
    
        #Try to get now thru the pageId
        try:
            pageReference = GeneralTopic.objects.get(pageid=queryResult['pageid'])
            #If suceeced, update title and urlTitle
            pageReference.title = queryResult['title']
            pageReference.urlTitle = queryResult['urlTitle']
            pageReference.save()

        #If it really does not exists, create it
        except GeneralTopic.DoesNotExist:

            #Create the new page
            pageReference = GeneralTopic(
                title=queryResult['title'], 
                pageid=queryResult['pageid'], 
                urlTitle=queryResult['urlTitle'])
            pageReference.save()

    #Return the create or got page
    return pageReference








#-------------------Not usefull any more-----------------------

#Function to get the page abstract links and the page db reference
def getAbstractLinks(page, lang):

    #Ensure the page is in quoted format and spaces are underscores
    #This is causing a bug, best is to trust for now that the correct link will be sent
    #page = quote(page).replace(" ", "_")

    queryResult = wikipedia_api.getPageAbstractLinks(page, lang)

    if queryResult['pageId'] == -1:
        print("-------------ERROR:--------------------")
        print(page)
        print(queryResult['error'])
        print("---------------------------------------")
        return None

    print(page)

    try:
        #Try to get the page reference thru its page url
        topicReference = GeneralTopic.objects.get(pageid=queryResult['pageId'])
    
    #If could not find it, create a new register
    except GeneralTopic.DoesNotExist:

        topicReference = GeneralTopic(
            title=queryResult['article'], 
            pageid=queryResult['pageId'], 
            urlTitle=queryResult['articleUrl'])
        topicReference.save()

    #Pass topic reference to the query result
    queryResult['topicReference'] = topicReference

    return queryResult


#Method to check whether and href exists in a linkobj array
def hrefExistsOn(array, href, lang):
    for elem in array:
        #Get the true link in case of redirection
        trueLinkHref = wikipedia_api.getTrueWikiLink(elem['href'], lang)
        #If the true link href is not valid, proceed next iteration
        if not trueLinkHref:
            continue

        elem['href'] = trueLinkHref
        if elem['href'] == href:
            return True
    
    return False