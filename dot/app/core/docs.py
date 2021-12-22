from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def docs(request):
    return render(request,'core/docs/docs.html')

@login_required
def issues(request):
    pass