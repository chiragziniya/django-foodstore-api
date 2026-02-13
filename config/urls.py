from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


def home(request):
    return redirect('/admin/')


urlpatterns = [
    path('', home),              # root → admin
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
]
