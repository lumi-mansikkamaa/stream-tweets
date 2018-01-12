import settings
import tweepy
from textblob import TextBlob
import dataset
import json

# connect to db
db = dataset.connect(settings.CONNECTION_STRING)

# override tweepy.StreamListener to add custom logic to on_status
class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        # don't process the retweets
        if hasattr(status, 'retweeted_status'):
            return
        print('Tweet: ' + status.text + '\nSource: ' + status.source + '\n')

        # extract the tweet properties for analysis
        description = status.user.description
        location = status.user.location
        text = status.text
        coords = status.coordinates
        name = status.user.screen_name
        user_created_at = status.user.created_at
        followers = status.user.followers_count
        id_str = status.id_str
        tweet_created_at = status.created_at
        retweets = status.retweet_count
        bg_color = status.user.profile_background_color

        # initialize the textblob class on the tweet & get the sentiment score from the class
        blob = TextBlob(text)
        sent = blob.sentiment

        if coords is not None:
            coords = json.dumps(coords)

        table = db[settings.TABLE_NAME]
        table.insert(dict(
            user_description=description,
            user_location=location,
            coordinates=coords,
            text=text,
            user_name=name,
            user_created=user_created_at,
            user_followers=followers,
            id_str=id_str,
            created=tweet_created_at,
            retweet_count=retweets,
            user_bg_color=bg_color,
            polarity=sent.polarity,
            subjectivity=sent.subjectivity
        ))

    def on_error(self, status_code):
        # catch 420 errors (rate limiting) & disconnect the stream
        if status_code == 420:
            return False


# set up tweepy to authenticate with Twitter
auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_SECRET)

# create an api object to fetch data from Twitter
api = tweepy.API(auth)

# stream the tweets
stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(track=settings.TRACK_TERMS)
