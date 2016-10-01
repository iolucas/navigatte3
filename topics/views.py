from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound

from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

from .models import GeneralTopic, UserTopic, BookReference, CourseReference, WebsiteReference, WikiArticle, WikiUrl, UserWikiArticle

from navigatte import  settings

from . import wikipedia_api2 as wikipedia_api

from urllib.parse import quote, unquote #Module to encode/decode urls strings

#Method to get the url from its label
from django.core.urlresolvers import reverse


from bs4 import BeautifulSoup
import urllib.request

import json


# Create your views here.

@login_required
def addNewUserArticle(request, userpage):

    #ON POST

    #If it was a new topic to be added
    if request.method == "POST" and 'topic_url_title' in request.POST and request.POST['topic_url_title']:
        
        pageUrl = unquote(request.POST['topic_url_title'])
        pageLang = "en" #if not 'lang' in request.POST else request.POST['lang']

        #Get the WikiArticle reference
        wikiArticle, created = getOrCreateArticleByUrl(pageUrl, pageLang, request.user)

        if wikiArticle == None:
            return invalidRequest("The wikiarticle reference returned is None. This is due an invalid url passed or an error during the request.")

        #Try to get this reference on the current user articles, if it does not exists, create a new with the reference
        try:
            request.user.userwikiarticle_set.get(wikiArticle=wikiArticle, deleted=False)
            return HttpResponse("User article already exists.")
        except UserWikiArticle.DoesNotExist:
            #If it does not exists, create it
            newUserWikiArticle = UserWikiArticle(wikiArticle=wikiArticle, createdBy=request.user)
            newUserWikiArticle.save()    

        return redirect('display_user_topics', userpage)


    #ON GET        

    if not 'search' in request.GET or not request.GET['search']:
        return render(request, "add-new-user-topic.html", {
            'noQuery': True,
            'userpage': userpage
        })

    resultObject = wikipedia_api.search(request.GET['search'])

    #If some error on search
    if resultObject == None:
        return HttpResponse("Error while completing the request.")

    return render(request, "add-new-user-topic.html",{
        'resultTopics': resultObject,
        'userpage': userpage
    })


def displayUserArticles(request, userpage):
    #Check whether the user exists and get it
    try:
        userpageRef = User.objects.get_by_natural_key(username=userpage)
    except User.DoesNotExist:
        return HttpResponseNotFound("User not found.")

    #return the request userpage, signaling whether this user is the owner or not

    #userpage is the current userpage displayed
    #Get all the subjects that are not deleted
    return render(request, 'user-topics-display.html', {
        'topic_list': userpageRef.userwikiarticle_set.filter(deleted=False),
        'userpage': userpage,
        'isOwner': userpageRef == request.user,
    })

def displayUserArticlesDetails(request, userpage, articleId):
    #Check whether the target user exists and get it
    try:
        userpageRef = User.objects.get_by_natural_key(username=userpage)
    except: #If it does not exists, return not found
        return HttpResponseNotFound("User not found.")

    #Try to get the user wiki article of the target user
    try:
        userWikiArticle = userpageRef.userwikiarticle_set.get(id=articleId)

        #Render the page with the target data
        return render(request, 'displayUserArticlesDetails.html', { 
            'name': userWikiArticle,
            'prereqs': userWikiArticle.preReqUserArticles.all(),    
            'articleId': articleId, 
            'userpage': userpage,
            'isOwner': userpageRef == request.user,         
        })

    except UserWikiArticle.DoesNotExist:
        return HttpResponseNotFound("User article not found.")




@login_required
def displayUserArticlesSearch(request, userpage, articleId):
    #Check whether the target user exists and get it
    try:
        userpageRef = User.objects.get_by_natural_key(username=userpage)
    except: #If it does not exists, return not found
        return HttpResponseNotFound("User not found.")

    #If this is not the logged user, return invalid request
    if userpageRef != request.user:
        return invalidRequest("You are attempting to access a search page that is not of your user.")

    #Try to get the user wiki article of the target user
    try:
        userWikiArticle = userpageRef.userwikiarticle_set.get(id=articleId)
    except UserWikiArticle.DoesNotExist:
        return HttpResponseNotFound("User article not found.")

    
    #Case there is a search query and it is valid
    if 's' in request.GET and request.GET['s']:

        resultObject = wikipedia_api.search(request.GET['s'])

        #If some error on search
        if resultObject == None:
            return HttpResponse("Error while completing the request.")

        return render(request, 'displayUserArticlesSearch.html', { 
            'name': userWikiArticle,
            'resultTopics': resultObject,
            'articleId': articleId, 
            'userpage': userpage,
            'isOwner': userpageRef == request.user,
            'noQuery': False        
        })





    #Filter wiki article abstract urls
    #Sugestions are important, so we filter not usefull links like those which return to the same page or the ones with a colon (:), that are wikipedia specific pages
    filteredAbstractUrls = []
    for abstUrl in userWikiArticle.wikiArticle.abstractUrls.all():
        #Not include urls that have colon included
        if ":" in abstUrl.urlPath:
            continue
        

        #Get abst links for each abst url if it does not have
        #Use them to organize the sugestions
        #if abstUrl.numberOfBacklinks == -1:
            #abstUrl.numberOfBacklinks = len(wikipedia_api.getPageBackLinks(abstUrl.urlPath, abstUrl.language))
            #abstUrl.save() #Save changes    

        filteredAbstractUrls.append({
            'title': abstUrl.urlPath.replace("_", " "),
            'url': abstUrl.urlPath,
            #'backlinksQty': abstUrl.numberOfBacklinks         
        })


    #Get all the references that have not the delete flag set
    return render(request, 'displayUserArticlesSearch.html', { 
        'name': userWikiArticle,
        'abstractLinks': filteredAbstractUrls,
        'articleId': articleId, 
        'userpage': userpage,
        'isOwner': userpageRef == request.user,
        'noQuery': True        
    })



@login_required
def addUserArticlePreRequisite(request, userpage, articleId):

    #implement deletation
    #improve page looks with space for user page permanent identification and article identification
    #clean useless stuff


    if not "prereqUrl" in request.POST:
        return invalidRequest("Invalid prereq add request. No prerequrl in POST method.")

    #Get target article url
    prereqUrl = request.POST["prereqUrl"]

    #Try to get the article reference passed on the current logged user
    try:
        targetUserArticle = request.user.userwikiarticle_set.get(id=articleId)

        #Get prereq article by its url 
        prereqArticle, created = getOrCreateArticleByUrl(prereqUrl, "en", request.user)

        #If the prereq article is not valid, raise exception
        if not prereqArticle:
            raise Exception("Invalid url passed to the query.")

        #Verify if the user have the prereq article, if not, add it     
        try:
            prereqUserArticle = request.user.userwikiarticle_set.get(wikiArticle=prereqArticle, deleted=False)
        except UserWikiArticle.DoesNotExist:
            #If it does not exists, create it
            prereqUserArticle = UserWikiArticle(wikiArticle=prereqArticle, createdBy=request.user)
            prereqUserArticle.save()    

        #Add the article to the prereq list of the target user article
        targetUserArticle.preReqUserArticles.add(prereqUserArticle)

        return redirect(reverse('displayUserArticlesDetails', kwargs={'userpage': userpage, 'articleId':articleId}))

    except UserWikiArticle.DoesNotExist:
        return invalidRequest("ArticleId not found for this user")

    except Exception as e:
        print(str(e))
        return invalidRequest(str(e))


    
    


def userArticleDetails(request, userpage):
    
    #Check whether the user exists and get it
    try:
        userpageRef = User.objects.get_by_natural_key(username=userpage)
    except:
        return HttpResponseNotFound("User not found.")   

    if 'id' in request.GET and request.GET['id']:

        try:
            topic_details = UserTopic.objects.get(id=request.GET['id'])

            #Get all the references that have not the delete flag set
            return render(request, 'user-topic-details.html', { 
                'name': topic_details, 
                'books': topic_details.books.all(),
                'courses': topic_details.courses.all(),    
                'websites': topic_details.websites.all(),
                'subject_id': request.GET['id'], 
                'userpage': userpage,
                'isOwner': userpageRef == request.user,         
            })

        except UserTopic.DoesNotExist:
            return HttpResponseNotFound("User topic not found")

    else: #If no id, return the topics list
        return redirect('display_user_topics')



#View to handle subject delete
@login_required
def deleteUserArticle(request, userpage):
    if request.method != 'POST':
        return HttpResponse("Invalid Request")

    #If a subject_id field is present and is valid (not empty)
    if 'articleId' in request.POST and request.POST['articleId']:

        try:
            userArticle = UserWikiArticle.objects.get(id=request.POST['articleId'], createdBy=request.user)

            #Set delete flag in the object and return subjects page
            #targetSubject.deleted = True

            print("test")
            userArticle.delete()
            #userArticle.save()

            return redirect('display_user_topics', userpage=userpage)

        except Exception as e:
            return invalidRequest("Error while deleting: " + str(e))

    return invalidRequest("No subject id or invalid subject id send.")





def deleteUserArticlePreRequisite(request, userpage, articleId):
    if request.method != 'POST':
        return invalidRequest("Invalid request. POST method expected.")

    if not validateEntries(request.POST, ["prereqId"]):
        return invalidRequest("Invalid request. prereqId missing or not valid.")

    prereqId = request.POST['prereqId']

    try:
        #Get userArticle reference

        userArticle = UserWikiArticle.objects.get(id=articleId, createdBy=request.user)

        #Get the prereq reference 
        prereqArticle = UserWikiArticle.objects.get(id=prereqId)

        #remove the reference from the subject
        userArticle.preReqUserArticles.remove(prereqArticle)
        
        #Save changes
        userArticle.save()

        return redirect(reverse('displayUserArticlesDetails', kwargs={'userpage': userpage, 'articleId':articleId}))

    except Exception as e:
        return invalidRequest("Error while deleting: " + str(e))


def displayUserMap(request, userpage):

    #Check whether the target user exists and get it
    try:
        userObj = User.objects.get_by_natural_key(username=userpage)
    except: #If it does not exists, return not found
        return HttpResponseNotFound("User not found.")


    #preReqUserArticles
    nodes = []
    links = []

    #Iterate thry all the user WikiArticles of this user 
    for userArticle in UserWikiArticle.objects.filter(createdBy=userObj):
        nodes.append({
            'name': str(userArticle),
            'localId': str(userArticle.id),
            'globalId': str(userArticle.id),
            'x': 0,
            'y': 0,
            'bgcolor':'#b3b3ff',
            'fgcolor':'#2d002d'
        })

        for prereq in userArticle.preReqUserArticles.all():
            links.append({
                'sourceId': str(prereq.id),
                'targetId': str(userArticle.id)
            })

        mapData = json.dumps({
            'nodes': nodes,
            'links': links    
        })

        print(mapData)

    # return HttpResponse(str({
    #     'nodes': nodes,
    #     'links': links    
    # }))


    return render(request, "displayUserMap.html", {
        'userpage': userpage,
        'mapData': mapData
    })



def getOrCreateArticleByUrl(url, lang, user):
    """Return article that the passed url-lang points to. If it does not exists, try to create it."""

    #Get or create the current url
    articleUrl, urlCreated = getOrCreateWikiUrl(url, lang, user)

    articleCreatedFlag = False

    #If the url was not created and it points to an article, return the articleUrl with a false created flag
    if not urlCreated and articleUrl.pointsTo:
        return articleUrl.pointsTo, articleCreatedFlag

    #If the url does not points to anything, query the url on wikipedia_api
    pageData = wikipedia_api.getPageAbstractLinks(url, lang)

    #If some error occured, return none
    if 'error' in pageData:
        return None, articleCreatedFlag

    #Try to get the article with pageId, if not found, create it 
    try:
        article = WikiArticle.objects.get(pageId=pageData['pageId'])
    except WikiArticle.DoesNotExist:
        articleCreatedFlag = True

        #Create title url (url used to access the articles)
        urlTitle = quote(pageData['title']).replace(" ", "_")

        #If the article does not exists, create it 
        article = WikiArticle(title=pageData['title'], titleUrl=urlTitle, pageId=pageData['pageId'], language=pageData['lang'], createdBy=user)

        article.save()

        #Filter abstract links repeated
        notRepeatedAbstractLinks = []
        for link in pageData['abstractLinks']:
            if not link in notRepeatedAbstractLinks:
                notRepeatedAbstractLinks.append(link)

        #Populate article abstract links with wikiurls
        for link in notRepeatedAbstractLinks:
            linkWikiUrl, urlCreated = getOrCreateWikiUrl(link, pageData['lang'], user)
            article.abstractUrls.add(linkWikiUrl)

        article.save()

    #Set the article to the current url and save
    articleUrl.pointsTo = article
    articleUrl.save()

    #return the article and the created flag
    return article, articleCreatedFlag


def getOrCreateWikiUrl(url, lang, user):
    """Return the passed arguments and if it not exists, try to create it."""

    createdFlag = False

    #Try to get the article wikiurl
    try:
        wikiUrl = WikiUrl.objects.get(urlPath=url, language=lang)
    #If it does not exists, create it and set created flag
    except WikiUrl.DoesNotExist:
        wikiUrl = WikiUrl(urlPath=url, language=lang, createdBy=user)
        wikiUrl.save()
        createdFlag = True

    return wikiUrl, createdFlag




def invalidRequest(debugMsg, nonDebugMsg = "Invalid Request"):
    """In case debug mode, returns the verbose passed string. If not in debug mode, return a simple invalid request message."""

    if settings.DEBUG:
        return HttpResponse(debugMsg) 

    return HttpResponse(nonDebugMsg) 

def validateEntries(collection, entries, blankAllowed = False):
    #iterate thru the entries
    for entry in entries:
        #if the entry does not exist, or is invalid (in case blankAllowed is false), return false
        if not entry in collection or not (collection[entry] or blankAllowed):
            return False
        
    return True