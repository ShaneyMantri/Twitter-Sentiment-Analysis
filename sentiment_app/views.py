from django.shortcuts import render
# Create your views here.
def home(request):
    return render(request, "sentiment_app/index.html")

def keyword_search(request):

    # if request.method =="POST":

    return render(request, "sentiment_app/keyword_analyse.html")