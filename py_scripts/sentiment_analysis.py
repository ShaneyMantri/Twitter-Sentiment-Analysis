
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import sentiment_mod as s



CONSUMER_API_KEY = ""
CONSUMER_API_SECRET_KEY = ""
ACCESS_TOKEN = ""
ACCESS_SECRET_TOKEN = ""


class listener(StreamListener):

    def on_data(self, data):
        try:
            all_data = json.loads(data)
            print(type(all_data))
            tweet = all_data["text"]
            sentiment_value, confidence = s.sentiment(tweet)
            print(tweet)
            print(sentiment_value, confidence)

            if confidence*100>=80:
                output=open("twitter_out.txt","a")
                output.write(sentiment_value+'\t'+str(confidence)+"\n")
                output.close()
            return True
        except Exception as e:
            print(str(e))
            return True
    def on_error(self, status):
        print(status)

auth = OAuthHandler(CONSUMER_API_KEY,CONSUMER_API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET_TOKEN)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=["Narendra Modi"])



print(s.sentiment("This movie was awesome. The acting was great, plot was wonderful, and there were pythons"))
