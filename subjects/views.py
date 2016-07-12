# Create your views here.

from django.http import HttpResponse

from django.shortcuts import render, redirect
#from django.views import generic

from .models import Subject

#Decorators for verification whether the user is logged in to use the view
from django.contrib.auth.decorators import login_required, user_passes_test



def loginCheck(user):
    return user.is_authenticated()

@user_passes_test(loginCheck, login_url="/login/")
def subjectsOwnerDisplay(request):
    #return the display owner page with the subjects that belongs to this owner
    return render(request, 'subjects-owner-display.html', {'subject_list': request.user.subject_set.all()})


@user_passes_test(loginCheck, login_url="/login/")
def subjectAdd(request):

    result_detail = None

    #Check whether a block_name var has been sent
    if 'subject_name' in request.POST:
        
        #If so, check if it is not empty
        if request.POST['subject_name']:
            #Create a new subject with this user as owner
            newSubject = Subject(name=request.POST['subject_name'], owner=request.user) 
            newSubject.save() #Register new subject
            result_detail = 'Subject created successfully.' #Set success msg
            return redirect("subjects_owner_display")
        else:
            result_detail = 'Error: Empty subject name.' #Set subject name empty msg

    #Return the result template
    return render(request, 'subjects-add.html', { 'result_detail': result_detail })

@user_passes_test(loginCheck, login_url="/login/")
def subjectsDetail(request):
    if 'id' in request.GET and request.GET['id']:

        try:
            subject_details = Subject.objects.get(id=request.GET['id'])

            return render(request, 'subjects-detail.html', { 
                'name': subject_details.name, 
                'books': subject_details.books.all(),
                'courses': subject_details.courses.all(),    
                'websites': subject_details.websites.all(),           
            })

        except Subject.DoesNotExist:
            return HttpResponse("Subject not found")

    else: #If no id, return the blocks list
        return redirect('subjects_owner_display')




    