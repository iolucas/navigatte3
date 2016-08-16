from django.shortcuts import redirect

def nvgttIndex(request):
    if request.user.is_authenticated():
        return redirect("home_index")

    return redirect('login_index')