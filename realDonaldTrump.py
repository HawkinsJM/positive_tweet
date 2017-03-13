import json

from positive_tweet import positive_tweet

import tweepy

# Import API Keys for the account to listen and post to.
# This account will look for tweets by the people it follows
# and then post positive versions of those tweets.
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

# Print the user name of the account.
api_acc = api.me()
print "Listening/Posting on account: " + api_acc.name


# Post positive version of tweet to account.
def post_tweet(original_tweet):
    n = 0
    ptweet = positive_tweet(original_tweet)
    change_made = ptweet[1]
    posttweet = ptweet[0]
    if change_made is True:  # if there are negative sentiment words replaced
        # Loop through and see if it comes up with a shorter tweet
        # if currently over 140 characters.
        while n < 100 and len(posttweet) > 140:
            n = n + 1
            ptweet = positive_tweet(original_tweet)
            change_made = ptweet[1]
            posttweet = ptweet[0]
    too_long = False
    if len(posttweet) > 140:
        too_long = True

    # If the original tweet is the same as the modified one
    # (no negative words found), retweet the original.
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
            print "Error posting tweet"
    else:
        print "All modified tweets generated were over 140 characters."


# Stream posts from twitter and post positive tweets.
# The following setup posts positive versions of any tweets of
# users followed by the account whos credentials we are using.
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        # When an event is detected print alert.
        print("New tweet detected")
        # Detect retweets so we can skip them.
        # This ignores retweets posted by users the account follows.
        retweet = False
        try:
            status.retweeted_status
            retweet = True
            print "Detected a RT, no further action"
        except AttributeError:
            pass
        # Detect mentions so we can skip them
        # This ignores mentions of the account whos credentials we are using
        # e.x. When people tweet at the account
        mention = False
        try:
            repl_id = status.in_reply_to_user_id_str
            if str(repl_id) == str(api_acc.id):
                mention = True
                print "Just a mention. No further action taken."
        except AttributeError:
            pass

        # If it is neither a retweet, a mention, or a post by the account
        # itself, then postive a postive version of the tweet.
        if (retweet is False and
                mention is False and
                status.user.id is not api_acc.id):
            post_tweet(status)
        elif retweet is False and mention is False:
            print "Post was by this account. It will be ignored"

# Initiate stream listener
myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
# Using userstream will get all tweets of users followed by the account
# of the api credentials we are using.
myStream.userstream("with=following")
