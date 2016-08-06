# Create your views here.

from navigatte import settings

from django.http import HttpResponse, HttpResponseNotFound

from django.shortcuts import render, redirect
#from django.views import generic

from .models import Topic, Subject, Book, Website, Course

#Decorators for verification whether the user is logged in to use the view
from django.contrib.auth.decorators import login_required, user_passes_test

#Method to get the url from its label
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User


from navigatte import wikipedia_api

def loginCheck(user):
    return user.is_authenticated()



#@user_passes_test(loginCheck, login_url="/login/")
def subjectsDisplay(request, userpage):

    #Check whether the user exists and get it
    try:
        userpageRef = User.objects.get_by_natural_key(username=userpage)
    except:
        return HttpResponseNotFound("User not found.")

    #return the request userpage, signaling whether this user is the owner or not

    #userpage is the current userpage displayed
    #Get all the subjects that are not deleted
    return render(request, 'subjects-display.html', {
        'subject_list': userpageRef.subject_set.filter(deleted=False),
        'userpage': userpage,
        'isOwner': userpageRef == request.user,
    })


@user_passes_test(loginCheck, login_url="/login/")
def subjectAdd(request, userpage):

    result_detail = None

    #Check whether a block_name var has been sent
    if 'subject_name' in request.POST:
        
        #If so, check if it is not empty
        if request.POST['subject_name']:
            #Create a new subject with this user as owner
            newSubject = Subject(name=request.POST['subject_name'], owner=request.user) 
            newSubject.save() #Register new subject
            result_detail = 'Subject created successfully.' #Set success msg
            return redirect("subjects_display", userpage=request.user)
        else:
            result_detail = 'Error: Empty subject name.' #Set subject name empty msg

    #Return the result template
    return render(request, 'subjects-add.html', { 
        'result_detail': result_detail, 
        'userpage': userpage,
    })

@user_passes_test(loginCheck, login_url="/login/")
def newUserTopic(request, userpage):

    #If it was a new topic to be added
    if request.method == "POST" and 'topic_url_title' in request.POST and request.POST['topic_url_title']:
        
        queryResult = wikipedia_api.query(request.POST['topic_url_title'])
        if queryResult == None:
            return HttpResponse("Invalid request")
        
        #Try to get topic, if not found, create a new
        try: 
            topicReference = Topic.objects.get(pageid=queryResult['pageid'])
        except Topic.DoesNotExist:
            topicReference = Topic(title=queryResult['title'], pageid=queryResult['pageid'])
            topicReference.save()

        #Add to the current user a reference to this topic

        return HttpResponse("Success")
        


    if not 'search' in request.GET or not request.GET['search']:
        return render(request, "new-user-topic.html", {
            'noQuery': True
        })

    resultObject = wikipedia_api.search(request.GET['search'])

    if resultObject == None:
        return HttpResponse("Error while completing the request.")

    return render(request, "new-user-topic.html",{
        'resultTopics': resultObject
    })



#@user_passes_test(loginCheck, login_url="/login/")
def subjectsDetail(request, userpage):
    
    #Check whether the user exists and get it
    try:
        userpageRef = User.objects.get_by_natural_key(username=userpage)
    except:
        return HttpResponse("User not found.")   

    if 'id' in request.GET and request.GET['id']:

        try:
            subject_details = Subject.objects.get(id=request.GET['id'])

            #Get all the references that have not the delete flag set
            return render(request, 'subjects-detail.html', { 
                'name': subject_details.name, 
                'books': subject_details.books.filter(deleted=False),
                'courses': subject_details.courses.filter(deleted=False),    
                'websites': subject_details.websites.filter(deleted=False),
                'subject_id': request.GET['id'], 
                'userpage': userpage,
                'isOwner': userpageRef == request.user,         
            })

        except Subject.DoesNotExist:
            return HttpResponse("Subject not found")

    else: #If no id, return the blocks list
        return redirect('subjects_owner_display')


@user_passes_test(loginCheck, login_url="/login/")
def subjectsReferenceAdd(request, userpage):
    if not "subject_id" in request.POST:
        return invalidRequest("Invalid reference add request. No subjectID in POST method.")

    
    subjectId = request.POST["subject_id"]

    #Check if the subject_id is valid and belongs to this user
    try:
        targetSubject = Subject.objects.get(id=subjectId)

        #If the target object owner is not the current user, finish with error
        if request.user != targetSubject.owner:
            return invalidRequest("Invalid reference add request. The target user owner of the subject is not the authenticated user.")

        #check which reference is being add
        if "course_name" in request.POST and request.POST["course_name"]:
            newCourse = Course(name=request.POST["course_name"])
            newCourse.save()
            #Add the new course to the target subject
            targetSubject.courses.add(newCourse)

        elif "book_title" in request.POST and request.POST["book_title"]:
            #Create new book (should be checked whether the desired exists before add a new)
            newBook = Book(name=request.POST["book_title"])
            newBook.save()
            targetSubject.books.add(newBook)

        elif "website_address" in request.POST and request.POST["website_address"]:
            newWebsite = Website(name=request.POST["website_address"])
            newWebsite.save()
            targetSubject.websites.add(newWebsite)

        else:
            #If no valid reference, return error
            return HttpResponse("Invalid reference add request (invalid reference).")

        return redirect(reverse('subjects_detail', kwargs={'userpage': userpage}) + "?id=" + subjectId)

    except Exception as e:
        return invalidRequest("Invalid reference add request. Exception: " + str(e))



#View to handle subject delete
def subjectDelete(request, userpage):
    if request.method != 'POST':
        return HttpResponse("Invalid Request")

    #If a subject_id field is present and is valid (not empty)
    if 'subject_id' in request.POST and request.POST['subject_id']:

        try:
            targetSubject = Subject.objects.get(id=request.POST['subject_id'])

            #Verifies if this subject does belongs to this user
            if request.user != targetSubject.owner:
                return invalidRequest("Invalid Delete. This subject does not belong to the signed in user.")

            #If it is the owner, set delete flag in the object and return subjects page
            targetSubject.deleted = True
            targetSubject.save()

            return redirect("subjects_display", userpage=userpage)

        except Exception as e:
            return invalidRequest("Error while deleting: " + str(e))

    return invalidRequest("No subject id or invalid subject id send.")



#View to handle subject reference delete
#For now remove the reference from the subject, later set a remove flag and keeps record
def subjectsReferenceDelete(request, userpage):
    if request.method != 'POST':
        return invalidRequest("Invalid request. POST method expected.")

    if not validateEntries(request.POST, ["subject_id", "reference_type", "reference_id"]):
        return invalidRequest("Invalid request. subject_id, reference_type or reference_id missing or not valid.")

    subjectId = request.POST['subject_id']
    referenceType = request.POST['reference_type']
    referenceId = request.POST['reference_id']

    try:
        #Get the target subject
        targetSubject = Subject.objects.get(id=subjectId)

        #Verifies if this subject does belongs to this user
        if request.user != targetSubject.owner:
            return invalidRequest("Invalid Delete. This subject does not belong to the signed in user.")
        
        #Get the target reference
        if referenceType == "website":
            targetReference = Website.objects.get(id=referenceId)
            #remove the reference from the subject
            targetSubject.websites.remove(targetReference)

        elif referenceType == "book":
            targetReference = Book.objects.get(id=referenceId)
            #remove the reference from the subject
            targetSubject.books.remove(targetReference)
        
        elif referenceType == "course":
            targetReference = Course.objects.get(id=referenceId)
            #remove the reference from the subject
            targetSubject.courses.remove(targetReference)
        else:
            return invalidRequest("Invalid Delete. Invalid type: " + referenceType)

        #save target subject
        targetSubject.save()

        return redirect(reverse('subjects_detail', kwargs={'userpage': userpage}) + "?id=" + subjectId)

    except Exception as e:
        return invalidRequest("Error while deleting: " + str(e))



def validateEntries(collection, entries, blankAllowed = False):
    #iterate thru the entries
    for entry in entries:
        #if the entry does not exist, or is invalid (in case blankAllowed is false), return false
        if not entry in collection or not (collection[entry] or blankAllowed):
            return False
        
    return True



def invalidRequest(debugMsg, nonDebugMsg = "Invalid Request"):
    if settings.DEBUG:
        return HttpResponse(debugMsg) 

    return HttpResponse(nonDebugMsg) 
       
    