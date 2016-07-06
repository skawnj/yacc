from django.http import HttpResponse
from django.template import Context, loader
from django.http import JsonResponse
from django.shortcuts import redirect
#import json
#from io import StringIO
import sys
from . import yacc
#import urllib.parse
from .models import *
import time

def _make_dict_readable(src_dict, indent_count = 0):
    buf = ''
    for key, value in src_dict.items():
        #buf += '\t' * indent_count + str(key) + ': '
        buf += '&nbsp;&nbsp;&nbsp;&nbsp;' * indent_count + str(key) + ': '
        if isinstance(value, dict):
            #buf += '\n'
            buf += '<br>'
            buf += _make_dict_readable(value, indent_count + 1)
        else:
            buf += str(value) + '<br>'
    return buf

def index(request, call_string = None, option = None):
    #print(search_restr('서여의도'))
    if call_string != None:
        print(call_string)
        #print(exec('yacc.yacc.' + urllib.parse.unquote(call_string, 'utf-8', 'ignore')))
        #exec('print({0})'.format('yacc.yacc.' + call_string))
        exec('res = yacc.' + call_string, globals())
        print(res)
        if not isinstance(res, dict):
            return HttpResponse(res)
        elif option == None:
            return JsonResponse(res)
        else: # option == 'readable':
            #old_stdout = sys.stdout
            #temp_io = StringIO()
            return HttpResponse(_make_dict_readable(res))
            #sys.stdout = old_stdout
            #return HttpResponse(res)
            #return HttpResponse(str(res))
    else:
        template = loader.get_template('func.html')
        context = Context(
            {'cstrings': ["get_restr_list(5, 'closest_it')"
                        , "get_restr_list(5, 'rating')"
                        , "get_restr_list(1, 'random')"
                        , "get_restr_list(10, 'random')"
                        , "get_restr_detail('R20160604010629860275', 'session_no_7777')"
                        , "get_user_info('session_no_7777')"
                        , "get_session_id('Double Goat')"
                        , "search_restr('서여의도')"
                        #, "search_restr('찌개')"
                        #, "_gen_nickname()"
                        #, "_get_timestamp()"
                        ]
            })
        return HttpResponse(template.render(context))
        #return HttpResponse(template)
        #return HttpResponse('abc')

def readable(request, call_string = None):
    return index(request, call_string, 'readable')

def test_page(request):
    #return HttpResponse('a message from the test page...')
    #restr = RestrBase.objects.create(rid = 'abcd' + str(time.time()))
    #restr.save()
    #restr_base = [i.rid for i in RestrBase.objects.all()]

    return HttpResponse(yacc._gen_db_schema())


'''
def index(request):
	template = loader.get_template('index.html')
	print('In index module.')
	print(request.GET)
	print(len(request.GET))
	context = Context({'txt': 'Wow, it is text from views.py.', 'get_data': request.GET})
	return HttpResponse(template.render(context))
	#return HttpResponse("Ok. I got it.")

def num_given(request):
	s = """show_msg()"""
	exec(s)
	return HttpResponse("Got number...")

def json_test(request):
	response = JsonResponse({'name': 'michael', 'age': '27', 'education': 'undergraduate', 'address': 'washington dc'})
	return response

def func(request, func_name):
	print(func_name)
	exec(func_name)
	return HttpResponse('Func...')
'''
