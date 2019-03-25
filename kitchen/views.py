from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    my_dict = {'insert_me': 'HELLO I AM FROM VIEWS.PY OF KITCHEN !'}
    return render(request, 'kitchen/index.html', context=my_dict)
