# Create your views here.

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect

from navigatte.settings import REGISTER_DISABLED

def register(request):
    if REGISTER_DISABLED:
        return HttpResponse("Register temporary disabled.")

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return render(request, "register_successful.html")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {
        'form': form,
    })