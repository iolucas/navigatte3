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


# Create your views here.

@login_required
def addNewUserTopic(request, userpage):

    #ON POST

    #If it was a new topic to be added
    if request.method == "POST" and 'topic_url_title' in request.POST and request.POST['topic_url_title']:
        
        pageUrl = unquote(request.POST['topic_url_title'])

        queryResult = wikipedia_api.getPageAbstractLinks(pageUrl)
        return HttpResponse(str(queryResult))


        if queryResult == None:
            return HttpResponse("Invalid request")

        for key in queryResult:
            print(key)
        
        #Try to get topic, if not found, create a new
        try: 
            topicReference = GeneralTopic.objects.get(pageid=queryResult['pageid'])
        except GeneralTopic.DoesNotExist:
            topicReference = GeneralTopic(title=queryResult['title'], 
                                                pageid=queryResult['pageid'], urlTitle=queryResult['urlTitle'])
            topicReference.save()

        #Try to get this reference on the current user topics, if it does not exists, create a new
        try:
            request.user.usertopic_set.get(generalTopic=topicReference, deleted=False)
            return HttpResponse("User topic already exists.")
        except UserTopic.DoesNotExist:
            #If it does not exists, create it
            newUserTopic = UserTopic(generalTopic=topicReference, owner=request.user)
            newUserTopic.save()

        return redirect('display_user_topics', userpage)

    #ON GET        

    if not 'search' in request.GET or not request.GET['search']:
        return render(request, "add-new-user-topic.html", {
            'noQuery': True,
            'userpage': userpage
        })

    resultObject = wikipedia_api.search(request.GET['search'])

    if resultObject == None:
        return HttpResponse("Error while completing the request.")

    return render(request, "add-new-user-topic.html",{
        'resultTopics': resultObject,
        'userpage': userpage
    })


def displayUserTopics(request, userpage):
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

def userTopicDetails(request, userpage):
    
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
def deleteUserTopic(request, userpage):
    if request.method != 'POST':
        return HttpResponse("Invalid Request")

    #If a subject_id field is present and is valid (not empty)
    if 'subject_id' in request.POST and request.POST['subject_id']:

        try:
            targetSubject = UserTopic.objects.get(id=request.POST['subject_id'], owner=request.user)

            #Verifies if this subject does belongs to this user
            #if request.user != targetSubject.owner:
                #return invalidRequest("Invalid Delete. This subject does not belong to the signed in user.")

            #If it is the owner, set delete flag in the object and return subjects page
            targetSubject.deleted = True
            targetSubject.save()

            return redirect('display_user_topics', userpage=userpage)

        except Exception as e:
            return invalidRequest("Error while deleting: " + str(e))

    return invalidRequest("No subject id or invalid subject id send.")



@login_required
def addUserTopicReference(request, userpage):
    if not "subject_id" in request.POST:
        return invalidRequest("Invalid reference add request. No subjectID in POST method.")

    
    subjectId = request.POST["subject_id"]

    #Check if the subject_id is valid and belongs to this user
    try:
        targetSubject = UserTopic.objects.get(id=subjectId, owner=request.user)

        #If the target object owner is not the current user, finish with error
        #if request.user != targetSubject.owner:
            #return invalidRequest("Invalid reference add request. The target user owner of the subject is not the authenticated user.")

        #check which reference is being add
        if "course_name" in request.POST and request.POST["course_name"]:
            newCourse = CourseReference(name=request.POST["course_name"])
            newCourse.save()
            #Add the new course to the target subject
            targetSubject.courses.add(newCourse)

        elif "book_title" in request.POST and request.POST["book_title"]:
            #Create new book (should be checked whether the desired exists before add a new)
            newBook = BookReference(name=request.POST["book_title"])
            newBook.save()
            targetSubject.books.add(newBook)

        elif "website_address" in request.POST and request.POST["website_address"]:
            
            #Try to get a reference to the address
            try:
                websiteRef = WebsiteReference.objects.get(address=request.POST["website_address"])
                targetSubject.websites.add(websiteRef)
            
            except WebsiteReference.DoesNotExist:

                #If it does not exists, create a new
                try:
                    #Get site data
                    websiteData = urllib.request.urlopen(request.POST["website_address"]).read()

                    #Parse site data to objects
                    websiteObj = BeautifulSoup(websiteData)

                    #Get a title if there is one on the page
                    if not websiteObj.title or websiteObj.title.string == None:
                        websiteName = request.POST["website_address"]
                    else:
                        websiteName = websiteObj.title.string

                #If the url is invalid
                except ValueError:
                    return HttpResponse("Invalid URL.")

                except Exception:
                    #If we can not retrieve site url, set the site title as the url
                    websiteName = request.POST["website_address"]

                newWebsite = WebsiteReference(name=websiteName, address=request.POST["website_address"])
                newWebsite.save()
                targetSubject.websites.add(newWebsite)

        else:
            #If no valid reference, return error
            return HttpResponse("Invalid reference add request (invalid reference).")

        return redirect(reverse('user_topic_details', kwargs={'userpage': userpage}) + "?id=" + subjectId)

    except Exception as e:
        #return invalidRequest("Invalid reference add request. Exception: " + str(e))
        raise e


#View to handle subject reference delete
#For now remove the reference from the subject, later set a remove flag and keeps record
def deleteUserTopicReference(request, userpage):
    if request.method != 'POST':
        return invalidRequest("Invalid request. POST method expected.")

    if not validateEntries(request.POST, ["subject_id", "reference_type", "reference_id"]):
        return invalidRequest("Invalid request. subject_id, reference_type or reference_id missing or not valid.")

    subjectId = request.POST['subject_id']
    referenceType = request.POST['reference_type']
    referenceId = request.POST['reference_id']

    try:
        #Get the target subject
        targetSubject = UserTopic.objects.get(id=subjectId, owner=request.user)

        #Verifies if this subject does belongs to this user
        #if request.user != targetSubject.owner:
            #return invalidRequest("Invalid Delete. This subject does not belong to the signed in user.")
        
        #Get the target reference
        if referenceType == "website":
            targetReference = WebsiteReference.objects.get(id=referenceId)
            #remove the reference from the subject
            targetSubject.websites.remove(targetReference)

        elif referenceType == "book":
            targetReference = BookReference.objects.get(id=referenceId)
            #remove the reference from the subject
            targetSubject.books.remove(targetReference)
        
        elif referenceType == "course":
            targetReference = CourseReference.objects.get(id=referenceId)
            #remove the reference from the subject
            targetSubject.courses.remove(targetReference)
        else:
            return invalidRequest("Invalid Delete. Invalid type: " + referenceType)

        #save target subject
        targetSubject.save()

        return redirect(reverse('user_topic_details', kwargs={'userpage': userpage}) + "?id=" + subjectId)

    except Exception as e:
        return invalidRequest("Error while deleting: " + str(e))


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

        #If the article does not exists, create it 
        article = WikiArticle(title=pageData['title'], pageId=pageData['pageId'], language=pageData['lang'], createdBy=user)

        article.save()

        #Populate article abstract links with wikiurls
        for link in pageData['abstractLinks']:
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