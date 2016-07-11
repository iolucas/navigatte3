# Create your views here.

from django.shortcuts import render
from django.views import generic

from .models import Block

#def index(request):
    #return render(request, 'blocks/blocks-area.html')

class IndexView(generic.ListView):
    template_name = 'blocks/blocks-area.html'
    context_object_name = 'block_list'

    def get_queryset(self):

        """
        Return the all the block objects
        """
        return Block.objects.all()


#View for add new blocks
#class AddFormView(generic.TemplateView):
    #template_name = 'blocks/blocks-add.html'

#View to handle new block post
class AddView(generic.FormView):
    template_name = 'blocks/blocks-add.html'

def addBlock(request):
    if request.method == 'POST':
        
        newBlock = Block(block_name='lucas123', block_description='ae1234567')
        newBlock.save()

    return render(request, 'blocks/blocks-add.html')