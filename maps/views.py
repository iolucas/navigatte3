from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User

# Create your views here.

@login_required
def mapsHome(request):
    return render(request, 'mapsHome.html')


@login_required
def displayUserArticle(request, userpage):
    #Check whether the user exists and get it
    try:
        userpageRef = User.objects.get_by_natural_key(username=userpage)
    except User.DoesNotExist:
        return HttpResponseNotFound("User not found.")

    #return the request userpage, signaling whether this user is the owner or not

    #userpage is the current userpage displayed
    #Get all the subjects that are not deleted
    return render(request, 'displayUserArticle.html', {
        'articleList': userpageRef.userwikiarticle_set.filter(deleted=False),
        'userpage': userpage,
        'isOwner': userpageRef == request.user,
    })


@login_required
def addNewUserArticle(request, userpage):

    #ON POST

    #If it was a new topic to be added
    if request.method == "POST" and 'topic_url_title' in request.POST and request.POST['topic_url_title']:
        
        queryResult = wikipedia_api.query(request.POST['topic_url_title'])
        if queryResult == None:
            return HttpResponse("Invalid request")
        
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
