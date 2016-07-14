from django.shortcuts import render, redirect

from django.core.urlresolvers import reverse

# Create your views here.

from django.http import HttpResponse

def userIndex(request, userpage):
    #return HttpResponse("User: " + userpage)
    return redirect(reverse('subjects_display', kwargs={'userpage': userpage}))
