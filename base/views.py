from django.conf import settings
from django.views.static import serve

def show_static(request):
    print('imglabeling/static/')
    path = request.GET.get('img', None)
    # path = request.data.copy()['img_name']
    print('path',path)
    return serve(**{'request':request, 'document_root':settings.FILES_PATH, 'path':path})

