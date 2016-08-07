from django.shortcuts import redirect

def nvgttIndex(request):
    if request.user.is_authenticated():
        return redirect("display_user_topics", request.user.username)

    return redirect('login_index')