import json

from positive_tweet import positive_tweet

import tweepy

# Import API Keys.
with open('positive_trump_creds.json') as creds:
    twitter_creds = json.load(creds)

# Access the twitter API.
consumer_key = twitter_creds['consumer_key']
consumer_secret = twitter_creds['consumer_secret']
access_token = twitter_creds['access_token']
access_token_secret = twitter_creds['access_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# Listen to test account.
username = 'jhtestacc'
user = api.get_user(username)

api_acc = api.me()
print "Now listening to account: " + username
print "Posting on account: " + api_acc.name


# Post positive version of tweet.
def post_tweet(original_tweet):
    n = 0
    ptweet = positive_tweet(original_tweet)
    change_made = ptweet[1]
    posttweet = ptweet[0]
    if change_made is True:
        # Loop through and see if it comes up with a shorter tweet
        # if over 140 characters.
        while n < 100 and len(posttweet) > 140:
            n = n + 1
            ptweet = positive_tweet(original_tweet)
            change_made = ptweet[1]
            posttweet = ptweet[0]
    too_long = False
    if len(posttweet) > 140:
        too_long = True

    # If the original tweet is the same as the modified one
    # (no ngative words found), retweet the original.
    # Otherwise, post the modified tweet.
    if change_made is False:
        print "Original Tweet was positive, so re-tweeted it."
        print "Original tweet text: " + original_tweet.text
        api.retweet(original_tweet.id)
    elif too_long is False and change_made is True:
        try:
            api.update_status(posttweet)
            print "New tweet posted"
            print "Original tweet text: " + original_tweet.text
            print "Positive tweet text: " + posttweet
        except:
            print "All modified tweets were too long, no revised tweet posted."
    else:
        print "No modified tweets that were short enough were found."


# Stream posts from twitter and post positive tweets.
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        # When an event is detected print the text of the event
        # and then post the positive tweet.
        print("New tweet detected")
        # Detect retweets so we can skip them
        retweet = False
        try:
            status.retweeted_status
            retweet = True
            print "Detected a RT, no further action"
        except AttributeError:
            pass
        # Detect mentions so we can skip them
        mention = False
        try:
            repl_id = status.in_reply_to_user_id_str
            if str(repl_id) == str(api_acc.id):
                mention = True
                print "Just a mention. No further action taken."
        except AttributeError:
            pass

        if (retweet is False and
                mention is False and
                status.user.id is not api_acc.id):
            post_tweet(status)
        elif retweet is False and mention is False:
            print "Post was by this account. It will be ignored"

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
myStream.userstream("with=following")
