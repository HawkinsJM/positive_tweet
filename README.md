#Positive Tweet
The goal if this project was to automatically replace all negative words in @realDonaldTrumps tweets with positive words and post them as [@pstvDonaldTrump](https://twitter.com/pstvDonaldTrump).

#Make Tweets Positive (Again)
A python program was developed to take any tweet, and replace all the negative sentiment words with positive sentiment words with a matching part-of-speech.
The positive_tweet function in positive_tweet.py performs this replacement. When fed a tweet object from tweepy it returns a two element list consisting of the text of the tweet with all negative words replaced by postive ones, and boolean value indicating if changes were made; True if words were replaced and False if no changes were made.

##realDonaldTrump
This was then applied to the account of realDonaldTrump. The twitter account @pstvDonaldTrump was created and set to follow @realDonaldTrump. The file realDonaldTrump.py uses the api credentials for @pstvDonaldTrump to listen for tweets by accounts it follows and then post positive versions of those tweets. It ignores retweets by accounts it follows.
