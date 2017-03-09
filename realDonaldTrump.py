import tweepy
from positive_tweet import positive_tweet
import HTMLParser
import json

# Import API Keys
with open('positive_trump_creds.json') as creds:    
    twitter_creds = json.load(creds)
    
#Access the twitter API
consumer_key = twitter_creds['consumer_key']
consumer_secret = twitter_creds['consumer_secret']
access_token = twitter_creds['access_token']
access_token_secret = twitter_creds['access_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

#Listen to test account
#username = 'realDonaldTrump'
username = 'jhtestacc'
user = api.get_user(username)

api_acc = api.me()
print "Now listening to account: " + username
print "Posting on account: " + api_acc.name

#post positive version of tweet
def post_tweet(original_tweet):    
    n=0
    ptweet = positive_tweet(original_tweet)
    change_made = ptweet[1]
    posttweet = ptweet[0]
    if change_made == True:
        #loop through and see if it comes up with a shorter tweet if over 140 characters
        while n <100 and len(posttweet)>140:
            n=n+1
            ptweet = positive_tweet(original_tweet)
            change_made = ptweet[1]
            posttweet = ptweet[0]
    too_long = False
    if len(posttweet)>140:
        too_long = True

#    print "orgingal tweet user id"
#    print original_tweet.user.name
#    print original_tweet.user.id
#    print type(original_tweet.user.id)
#    print"user id"
#    print user.name
#    print user.id
#    print type(user.id)
#    print"me id"
#    print api_acc.name
#    print api_acc.id
#    print type(api_acc.id)

 #If the original tweet is the same as the modified one (no ngative words found), retweet the original.  Otherwise, post the modified tweet.
    if change_made == False:
        print "Original Tweet was positive, so re-tweeted it."
        print "Original tweet text: " + original_tweet.text
        api.retweet(original_tweet.id)
    elif too_long == False and change_made == True:
        try:
            api.update_status(posttweet)
            print "New tweet posted"
            print "Original tweet text: " + original_tweet.text
            print "Positive tweet text: " + posttweet
        except:
            print "All modified tweets were too long, no revised tweet posted."   
    else:
        print "No modified tweets that were short enough were found."
        
#Stream posts from twitter and post positive tweets
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        #when an event is detected print the text of the event and then post the positive tweet
        print("New tweet detected")
    #detect retweets so we can skip them        
        retweet = False
        try:
            status.retweeted_status
            retweet = True
            print "Detected a RT, no further action"
        except AttributeError:
            pass
#detect mentions so we can skip them 
        mention = False
        try:
            repl_id = status.in_reply_to_user_id_str
            if str(repl_id) == str(api_acc.id):
                mention = True
                print "Just a mention not a post by followed user. No further action"
        except AttributeError:
            pass
        
        if retweet == False and mention == False and status.user.id != api_acc.id:
            post_tweet(status)
        elif retweet == False and mention == False:
            print "Post was by this account. It will be ignored"

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
#myStream.filter(follow=[str(user.id)])
myStream.userstream("with=following")
