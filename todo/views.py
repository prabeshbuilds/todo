from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Todo

def index(request):
    todos = Todo.objects.all()

    if request.method == "POST":
        title = request.POST.get("title")
        if title:
            Todo.objects.create(title=title)
            return redirect('index')

    return render(request, "todo/index.html", {"todos": todos})


def complete(request, pk):
    todo = Todo.objects.get(id=pk)
    todo.completed = True
    todo.save()
    return redirect('index')


def delete(request, pk):
    todo = Todo.objects.get(id=pk)
    todo.delete()
    return redirect('index')

def health(request):
    return JsonResponse({"status": "UP"})