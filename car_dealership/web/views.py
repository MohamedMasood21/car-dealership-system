from django.contrib.auth import authenticate, login
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q

from .forms import UserForm
from .models import Car, TestDrive, Order


# Create your views here.
def index(request):
    return render(request, 'web/index.html')


def login_user(request):
    if request.user.is_authenticated:
        return redirect('web:cars')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('web:cars')
            else:
                return render(request, 'web/login.html', {'error_message': 'Your account has not been activated!'})
        else:
            return render(request, 'web/login.html', {'error_message': 'Invalid login'})
    return render(request, 'web/login.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('web:cars')
    uform = UserForm(request.POST or None)
    if uform.is_valid():
        user = uform.save(commit=False)
        username = uform.cleaned_data['username']
        password = uform.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('web:cars')

    context = {
        "uform": uform,
    }

    return render(request, 'web/register.html', context)


def cars_page(request, pg=1):

    # Each page has 9 requests. That is fixed.
    start = (pg-1) * 9
    end = start + 9

    car_list = Car.objects.all()[start:end]
    context = {
        'cars': car_list
    }

    return render(request, 'web/cars.html', context)


def car_search(request):
    if request.method == 'GET':
        if request.GET.get('search'):
            search = request.GET.get('search')
        else:
            search = 0
        if request.GET.get('start'):
            start = int(request.GET.get('start'))
        else:
            start = ''
        if request.GET.get('end'):
            end = int(request.GET.get('end'))
        else:
            end = 9

        objs = Car.objects.filter(
            Q(brand__icontains=search) | Q(name__icontains=search)
        )[start:end]
        data = serializers.serialize('json', objs)
        return HttpResponse(data)


def cars(request):
    if request.method == 'GET':
        if request.GET.get('start'):
            start = int(request.GET.get('start'))
        else:
            start = 0
        if request.GET.get('end'):
            end = int(request.GET.get('end'))
        else:
            end = 9
        if request.GET.get('make'):
            make = request.GET.get('make')
            if make == 'all':
                make = ''
        else:
            make = ''
        if request.GET.get('cost_min'):
            cost_min = int(float(request.GET.get('cost_min')))
        else:
            cost_min = 0
        if request.GET.get('cost_max'):
            cost_max = int(float(request.GET.get('cost_max')))
        else:
            cost_max = 999999999
        if request.GET.get('fuel'):
            fuel = request.GET.getlist('fuel')
        else:
            fuel = ['petrol', 'diesel']

        if len(fuel) > 1:
            objs = Car.objects.filter(
                Q(car_make__icontains=make) &
                Q(price__gte=cost_min) &
                Q(price__lte=cost_max) &
                (Q(fuel__icontains=fuel[0]) | Q(fuel__icontains=fuel[1]))
            )[start:end]

        else:
            objs = Car.objects.filter(
                car_make__icontains=make,
                price__gte=cost_min,
                price__lte=cost_max,
                fuel__icontains=fuel[0]
            )[start:end]

    else:
        objs = Car.objects.all()[:9]

    data = serializers.serialize('json', objs)
    return HttpResponse(data)
