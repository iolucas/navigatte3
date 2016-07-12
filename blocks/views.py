# Create your views here.

from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.views import generic

from .models import Block

#Decorators for verification whether the user is logged in to use the view
from django.contrib.auth.decorators import login_required, user_passes_test



def loginCheck(user):
    return user.is_authenticated()

@user_passes_test(loginCheck, login_url="/login/")
def blocksDisplay(request):
    return render(request, 'blocks/blocks-area.html', {'block_list': Block.objects.all()})


@user_passes_test(loginCheck, login_url="/login/")
def blockAdd(request):

    result_detail = None

    #Check whether a block_name var has been sent
    if 'block_name' in request.POST:
        
        #If so, check if it is not empty
        if request.POST['block_name']:
            newBlock = Block(name=request.POST['block_name']) #Create a new block
            newBlock.save() #Register new block
            result_detail = 'Block created successfully.' #Set success msg
        else:
            result_detail = 'Error: Empty block name.' #Set block name empty msg

    #Return the result template
    return render(request, 'blocks/blocks-add.html', { 'result_detail': result_detail })

@user_passes_test(loginCheck, login_url="/login/")
def blockDetails(request):
    if 'id' in request.GET and request.GET['id']:

        try:
            block_details = Block.objects.get(id=request.GET['id'])

            return render(request, 'blocks/block-details.html', { 
                'name': block_details.name, 
                'books': block_details.books.all(),
                'courses': block_details.courses.all(),    
                'websites': block_details.websites.all(),           
            })

        except Block.DoesNotExist:
            return HttpResponse("Block not found")

    else: #If no id, return the blocks list
        return redirect('blocks_index')




    