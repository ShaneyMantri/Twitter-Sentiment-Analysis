# imports for analysis of tweets
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from tweepy import Cursor, Stream, API  # Cursor used for timeline tweets on our profile, friend's profile
from tweepy import OAuthHandler  # Used for authentication
from tweepy.streaming import StreamListener  # Used to listen to tweet based on keywords or hash tags
from . import twitter_credentials  # For twitter API credentials
from textblob import TextBlob
import re  # Regex module
# from . import sentiment_mod as s

"""Twitter Client"""
class TwitterClient:

    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user  # user timeline for specified user

    def get_twitter_client_api(self):  # used to return the twitter api for further referencing
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):  # num_tweets for number of tweets we want to extract
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(
                num_tweets):  # user_timeline defaults to ourselves if we do not specify the user whose timeline is to be accessed
            tweets.append(tweet)

        return tweets

    def get_friend_list(self, friend_num):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(friend_num):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, tweet_num):  # Gives tweets present on the home page (not profile page)
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(tweet_num):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets



"""Creating a class for authentication"""
class TwitterAuthenticator:

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_API_KEY,
                            twitter_credentials.CONSUMER_API_KEY_SECRET)  # Responsible for authentication

        auth.set_access_token(twitter_credentials.ACCESS_TOKEN,
                              twitter_credentials.ACCESS_TOKEN_SECRET)  # Initialized the authentication object
        return auth



"""Creating class to stream and processing live tweets and save to text, JSON files"""
class TwitterStreamer:

    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()  # Creating an authenticator object

    def stream_tweets(self, fetched_tweets_filename, keyword_list):
        """This handles twitter authentication and the connection to the twitter streaming API"""
        listener = TwitterListener(fetched_tweets_filename)  # Responsible for live streaming of tweets (Deal with data and error)
        auth = self.twitter_authenticator.authenticate_twitter_app()  # Initializing the authentication object
        stream = Stream(auth, listener)

        stream.filter(track=keyword_list)  # Filter tweets by keywords



"""Creating a basic listener class for writing tweet data in a file, handle error"""
"""Over riding methods from StreamListener"""
class TwitterListener(StreamListener):

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename  # Initializing the object with the filename
        self.count = 0
        self.wrapper = []

    def on_data(self, data):  # Takes in data from StreamListener
        try:
            self.count+=1
            all_data = json.loads(data)
            # json_tweet = json.dumps(all_data, indent=4)
            self.wrapper.append(all_data)
            # print(self.wrapper[0])
            if self.count<twitter_credentials.MAX_COUNT_MODE_1:  # Setting limit on max number of tweets from keywords
                return True
            else:
                with open(self.fetched_tweets_filename, "w") as tf:
                    dumping_list = json.dumps(self.wrapper)
                    tf.write(dumping_list)
                return False
        except Exception as e:
            print("Error in on_data method : {}".format(str(e)))  # Printing exception
        return True

    def on_error(self, status):  # Triggered when error occurs and prints status
        if status == 420:  # Violation of twitter norms (rate limit occurs)
            return False  # Kill the connection
        print(status)



"""Functionality for analysing and categorising contents from tweets"""
class TweetAnalyser():

    def clean_tweet(self, tweet):  # Regex operation performing function to clean the tweets from stop words, hyperlinks etc.
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())



    def analyse_with_sentiment_mode(self, tweet):
        analysis, confidence = s.sentiment(tweet)

        return str(analysis)+"---"+str(confidence)


    def analyse_sentiment(self, tweet):  # Uses textblob for analysing the sentiment of the tweet
        analysis = TextBlob(self.clean_tweet(tweet))
        
        # Polarity tells us about the polarity of the tweet (whether it's positive or negative or neutral)
        if analysis.sentiment.polarity>0 and analysis.sentiment.polarity<=0.3:
            return "Low Positive"
        elif analysis.sentiment.polarity>0.3 and analysis.sentiment.polarity<=0.5:
            return "Moderately Positive"
        elif analysis.sentiment.polarity>0.5:
            return "Highly Positive"


        elif analysis.sentiment.polarity==0:
            return "Neutral"


        elif analysis.sentiment.polarity<0 and analysis.sentiment.polarity>=-0.3:
            return "Low Negative"
        elif analysis.sentiment.polarity<-0.3 and analysis.sentiment.polarity>=-0.5:
            return "Moderately Negative"
        elif analysis.sentiment.polarity<-0.5:
            return "Highly Negative"


        return "Neutral"


    def tweets_to_dataframe_mode1(self, tweets_dict):
        tweets = []
        for i in range(len(tweets_dict)):
            tweets.append(tweets_dict[i])
        df = pd.DataFrame([tweet['text'] for tweet in tweets], columns=["tweet"])
        df['id'] = np.array([tweet['id'] for tweet in tweets])
        df['len'] = np.array([len(tweet['text']) for tweet in tweets])
        df['date'] = np.array([tweet['created_at'] for tweet in tweets])
        df['source'] = np.array([tweet['source'] for tweet in tweets])
        df['likes'] = np.array([tweet['favorite_count'] for tweet in tweets])
        df['retweets'] = np.array([tweet['retweet_count'] for tweet in tweets])
        return df




    def tweets_to_dataframe_mode2(self, tweets):
        df = pd.DataFrame([tweet.text for tweet in tweets], columns=["tweet"])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df


    def visualise(self, df):
        """Time series visualisation"""

        time_likes = pd.Series(data=df['likes'].values, index=df['date'])  # Time series for number of likes
        time_likes.plot(figsize=(16, 4), color="r")
        plt.show()

        time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])  # Time series for number of retweets
        time_retweets.plot(figsize=(16, 4), color="r")
        plt.show()

        time_likes = pd.Series(data=df['likes'].values, index=df['date'])  # Time series for both number of likes and retweets
        time_likes.plot(figsize=(16, 4), label="likes", legend=True)
        time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
        time_retweets.plot(figsize=(16, 4), label="retweet", legend=True)
        plt.show()  # Combining plots for likes and retweets



def keyword_analyse(keywords):
    tweet_analyser = TweetAnalyser()
    # keyword_list = ["donald trump", "hillary clinton", "barak obama","bernie sanders"]  # list of keywords or hash tags for filtering tweets
    fetched_tweets_filename = "tweets.json"  # File for writing the tweets
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(fetched_tweets_filename,
                                   keywords)  # Creating and passing args to a streamer object
    tweetsList = []
    with open('tweets.json') as f:
        data = json.loads(f.read())

    df = tweet_analyser.tweets_to_dataframe_mode1(data)
    df['sentiment'] = np.array([tweet_analyser.analyse_sentiment(tweet) for tweet in df['tweet']])
    df = list(df.T.to_dict().values())
    return df





def profile_analyse(screen_name, count):
    tweet_analyser = TweetAnalyser()
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()  # get the api for referencing

    tweets = api.user_timeline(screen_name=screen_name,
                               count=count)  # screen_name = user and count = number of tweets
    # print(tweets[0].text)
    # print(type(tweets[0]))
    df = tweet_analyser.tweets_to_dataframe_mode2(tweets)
    df['sentiment'] = np.array([tweet_analyser.analyse_sentiment(tweet) for tweet in df['tweet']])
    df = list(df.T.to_dict().values())
    return df

if __name__ == "__main__":
    tweet_analyser = TweetAnalyser()
    mode = int(input("Enter 1 for keyword based search and 2 for profile based search\n"))
    if mode==1:
        keyword_list = ["donald trump", "hillary clinton", "barak obama","bernie sanders"]  # list of keywords or hash tags for filtering tweets
        fetched_tweets_filename = "tweets.json"  # File for writing the tweets
        twitter_streamer = TwitterStreamer()
        twitter_streamer.stream_tweets(fetched_tweets_filename, keyword_list)  # Creating and passing args to a streamer object
        tweetsList = []
        with open('tweets.json') as f:
            data = json.loads(f.read())


        df = tweet_analyser.tweets_to_dataframe_mode1(data)



    elif mode==2:
        twitter_client = TwitterClient()
        api = twitter_client.get_twitter_client_api()  # get the api for referencing

        tweets = api.user_timeline(screen_name="realDonaldTrump", count=200)  # screen_name = user and count = number of tweets
        df = tweet_analyser.tweets_to_dataframe_mode2(tweets)


    """Creating another column for sentiment analysis for each tweet"""
    df['sentiment'] = np.array([tweet_analyser.analyse_sentiment(tweet) for tweet in df['tweet']])


    df['sentiment'] = np.array([tweet_analyser.analyse_sentiment(tweet) for tweet in df['tweet']])

    print(df.head(10))
