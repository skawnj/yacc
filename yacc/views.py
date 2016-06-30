from django.http import HttpResponse
from django.template import Context, loader
from django.http import JsonResponse
from django.shortcuts import redirect
import sys
#import urllib.parse

def index(request):
    return redirect('/func')
    #return HttpResponse('index page')
