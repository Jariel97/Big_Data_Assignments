from kafka import KafkaProducer
import kafka
import json
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

consumer_key = "ed2wTAjHXE97d9XtRAtfJ57Jx"
consumer_secret = "7LpNsSs1kVcnjSWaxvOTePDiQjX7XrYiXbvuW96VJeXjhnxDvy"
access_token = "1360952139707678722-g6iiSvGKSbfi9wpcVqsGwTrQVhoFmR"
access_secret = "Z5avWLt4XEWrzp9RWpwTnXEyHkBFHnqZBc0Mj8C4ihZdp"


hashtag = "corona"
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)
class KafkaPushListener(StreamListener):
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

    def on_data(self, data):
        self.producer.send("twitter_stream_" + hashtag +"tweets", data.encode('utf-8'))
        print(data)
        return True

    def on_error(self, status):
        print(status)
        return True


twitter_stream = Stream(auth, KafkaPushListener())

hashStr = "#"+ hashtag

twitter_stream.filter(track=[hashStr])
