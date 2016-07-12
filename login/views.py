from django.shortcuts import render, redirect

# Create your views here.

from django.contrib import auth

#Import function to get the url from its label
from django.core.urlresolvers import reverse


def login(request):

    login_error = False

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_active:
            # Correct password, and the user is marked "active"
            auth.login(request, user)

            #Get the next page to be redirected
            next = request.GET.get('next', reverse('subjects_owner_display'))

            # Redirect to the next page
            return redirect(next)

        #If the user is not active or it is none, set login error true
        login_error = True

    return render(request, 'login.html', { 'login_error': login_error })



def logout(request):
    auth.logout(request)

    # Redirect to the blocks page
    return redirect('login_index')