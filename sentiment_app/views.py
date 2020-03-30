from django.shortcuts import render
from py_scripts import tweepy_streamer
# Create your views here.
def home(request):
    return render(request, "sentiment_app/index.html")

def keyword_search(request):
    if request.method=="POST":
        keyword = request.POST.get("keywords")
        tweet_details = tweepy_streamer.keyword_analyse(str(keyword))
        context = {"context":tweet_details}
        return render(request, "sentiment_app/analysis.html", context)


    return render(request, "sentiment_app/keyword_analyse.html")


def profile_search(request):

    if request.method=="POST":
        profilename = request.POST.get("profilename")
        tweet_details = tweepy_streamer.profile_analyse(str(profilename), 100)
        context = {"context":tweet_details}
        return render(request, "sentiment_app/analysis.html", context)

    return render(request, "sentiment_app/profile_analyse.html")