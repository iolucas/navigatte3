from django.shortcuts import redirect

def nvgttIndex(request):
    return redirect("home_index")
    if request.user.is_authenticated():
        return redirect("display_user_topics", userpage=request.user.username)

    return redirect('login_index')