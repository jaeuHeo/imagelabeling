# -*- coding: utf-8 -*-

from django.conf.urls import url
from imglabeling import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    url(r'^alivecheck',views.get_alive_check),
    url(r'^saveImage/',views.saveImage),
    url(r'^lookUp/',views.lookUp),
    url(r'^deleteImage/',views.deleteImage),
    url(r'^segmentImage/',views.segmentImage),
    url(r'^segmentBoundary/',views.segmentBoundary),
]
