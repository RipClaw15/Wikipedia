from django.shortcuts import render
from django import template
from django.template.defaultfilters import stringfilter
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

import random
import markdown as md

from . import util

class createPageForm(forms.Form):
    title = forms.CharField(label="title")
    content = forms.CharField(label="content")

class editPageForm(forms.Form):
    title = forms.CharField(label="title", required=True)
    #content = forms.CharField(label="content")

register = template.Library()


@register.filter()
@stringfilter
def markdown(value):
    return md.markdown(value, extensions=['markdown.extensions.fenced_code'])

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, name):
    lowercaseResults = [item.lower() for item in util.list_entries()]
    if name.lower() in lowercaseResults:
        return render(request, "encyclopedia/wiki/entry.html", {
            "entry": markdown(util.get_entry(name)),
            "title": name

    })

def search(request):
    if request.method == "GET":
        q = request.GET.get('q', '')
        lowercaseResults = [item.lower() for item in util.list_entries()]
        lowercase_dict = {item.lower(): item for item in util.list_entries()}
        subStrings = [lowercase_dict[item] for item in lowercaseResults if q.lower() in item]
        if q.lower() in lowercaseResults:
            return render(request, "encyclopedia/wiki/entry.html", {
            "entry": markdown(util.get_entry(q))
        })
        elif subStrings:
            return render(request, "encyclopedia/index.html", {
            "entries": subStrings
            })
        else:
            
            return render(request, "encyclopedia/error.html", {
            "error": f"No {q} page found."
            })
    else:
            return render(request, "encyclopedia/error.html", {
            "error": "Method is not GET!"
            })


def create(request):
    if request.method == "POST":
        form = createPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            lowercaseResults = [item.lower() for item in util.list_entries()]
            if title.lower() in lowercaseResults:
                return render(request, "encyclopedia/error.html", {
            "error": "Page already exists"
            })
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            
            return HttpResponseRedirect(reverse(entry, args=[title]))
        else:
            return render(request, "encyclopedia/error.html", {
            "error": "Form is not valid!"
            })
    return render(request, "encyclopedia/create.html")

def edit(request):
    if request.method == "POST":
        form = editPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = util.get_entry(title)
            edit = request.POST.get("edit")
            
            if edit == "True":
                content = request.POST.get('content').replace('\r\n', '0')
                content = request.POST.get('content')
                
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse(entry, args=[title]))
            return render(request, "encyclopedia/edit.html", {
                "content":content,
                "title":title
                })
        else:
            return render(request, "encyclopedia/error.html", {
            "error": "Form is not valid!"
            })
    return render(request, "encyclopedia/index")
    

def randomPage(request): 
    rnd = random.choice(util.list_entries())
    return render(request, "encyclopedia/wiki/entry.html",{
        "entry": markdown(util.get_entry(rnd)),
        "title": rnd
    }) 

