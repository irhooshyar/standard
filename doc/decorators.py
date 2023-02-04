from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import *


def unathenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.COOKIES.get('username'):
            return redirect('index')
        else:
            return view_func(request, *args, **kwargs)
        
    return wrapper_func


def is_login(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.COOKIES.get('username'):
            return redirect('index')
        else:
            return view_func(request, *args, **kwargs)
        
    return wrapper_func


def allowed_users(*allowed_panels):
    def decorators(view_func):
        def wrapper_func(request, *args, **kwargs):
            username = request.COOKIES.get('username')
            if not username:
                return redirect('index')
            try:
                user = User.objects.all().get(username=username)
                if user.is_super_user:
                    return view_func(request, *args, **kwargs)
                panels = UserPanels.objects.all().filter(user=user)
                for panel in panels:
                    if panel.panel.panel_english_name in allowed_panels:
                        return view_func(request, *args, **kwargs)
                return render(request, 'doc/notfound.html')

            except: # if user not exist
                return render(request, 'doc/notfound.html')

        return wrapper_func
    return decorators