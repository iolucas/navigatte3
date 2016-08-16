from django.shortcuts import render

from django.http import HttpResponse

from navigatte import wikipedia_api

import re

def homeIndex(request):

    result = wikipedia_api.getPageAbstractLinks("Contabilidade", "pt")

    resultStr = "<br><br>".join(result)

    return HttpResponse(resultStr)

    #if request.user.is_authenticated():
        #return redirect("display_user_topics", request.user.username)

   # return redirect('login_index')