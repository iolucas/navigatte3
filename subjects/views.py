# Create your views here.

from navigatte import settings

from django.http import HttpResponse

from django.shortcuts import render, redirect
#from django.views import generic

from .models import Subject, Book, Website, Course

#Decorators for verification whether the user is logged in to use the view
from django.contrib.auth.decorators import login_required, user_passes_test

#Method to get the url from its label
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

def loginCheck(user):
    return user.is_authenticated()

#@user_passes_test(loginCheck, login_url="/login/")
def subjectsDisplay(request, userpage):

    #Check whether the user exists and get it
    try:
        userpageRef = User.objects.get_by_natural_key(username=userpage)
    except:
        return HttpResponse("User not found.")   

    #return the request userpage, signaling whether this user is the owner or not

    #userpage is the current userpage displayed
    return render(request, 'subjects-display.html', {
        'subject_list': userpageRef.subject_set.all(),
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

            return render(request, 'subjects-detail.html', { 
                'name': subject_details.name, 
                'books': subject_details.books.all(),
                'courses': subject_details.courses.all(),    
                'websites': subject_details.websites.all(),
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
        if settings.DEBUG:
            return HttpResponse("Invalid reference add request. No subjectID in POST method.")
        else:
            return HttpResponse("Invalid Request")
    
    subjectId = request.POST["subject_id"]

    #Check if the subject_id is valid and belongs to this user
    try:
        targetSubject = Subject.objects.get(id=subjectId)

        #If the target object owner is not the current user, finish with error
        if request.user != targetSubject.owner:
            if settings.DEBUG:
                return HttpResponse("Invalid reference add request. The target user owner of the subject is not the authenticated user.")
            else:
                return HttpResponse("Invalid Request")

        #check which reference is being add
        if "course_name" in request.POST:
            #Create new book (should be checked whether the desired exists before add a new)
            newCourse = Course(name=request.POST["course_name"])
            newCourse.save()
            #Add the new course to the target subject
            targetSubject.courses.add(newCourse)

        elif "book_title" in request.POST:
            newBook = Book(name=request.POST["book_title"])
            newBook.save()
            targetSubject.books.add(newBook)

        elif "website_address" in request.POST:
            newWebsite = Website(name=request.POST["website_address"])
            newWebsite.save()
            targetSubject.websites.add(newWebsite)

        else:
            #If no valid reference, return error
            return HttpResponse("Invalid reference add request (invalid reference).")

        return redirect(reverse('subjects_detail', kwargs={'userpage': userpage}) + "?id=" + subjectId)

    except Exception as e:
        if settings.DEBUG:
            return HttpResponse("Invalid reference add request. Exception: " + str(e))
        else:
            return HttpResponse("Invalid Request")
        



    