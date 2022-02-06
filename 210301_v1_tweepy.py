#Libraries
import tweepy
import datetime
import csv
from textblob_de import TextBlobDE as TextBlob
import re # for using regular expressions


# pip install -U textblob-de
# python -m textblob.download_corpora

# Rate Limit: The user Tweet timeline endpoint is a REST endpoint that receives a single path parameter to indicate the desired user (by user ID).
# Endpoint can return only the 3,200 most recent Tweets, Retweets, replies.


"""
Authentification information provided by the twitter application
"""
consumer_key = ""
consumer_secret = ""
access_key = "-"
access_secret = ""

startDate = datetime.datetime(2019, 1, 1, 0, 0, 0)
endDate =   datetime.datetime(2021, 3, 1, 0, 0, 0)

def get_all_tweets(screen_name):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    alltweets = []

    ## 200 counts per interation is the maximum
    new_tweets = api.user_timeline(screen_name = screen_name,count=200, tweet_mode="extended")

    for tweet in new_tweets:
        if tweet.created_at < endDate and tweet.created_at > startDate:
            alltweets.append(tweet)
            oldest = alltweets[-1].id - 1



    breakcon = 0
    #collect tweets until there are no more tweets
    while len(new_tweets) > 0:
    #while len(new_tweets) > 0:
        print(f"getting tweets before {oldest}")

        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest, tweet_mode="extended")
        for tweet in new_tweets:
            if tweet.created_at < endDate and tweet.created_at > startDate:
                alltweets.append(tweet)

        # wenn keine neue Tweets entsprechend Datum mehr hinzukommen: raus aus Schleife
        if breakcon == len(alltweets):
            break

        #save most recent tweets
        #alltweets.extend(new_tweets)

        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        breakcon = len(alltweets)

        print(f"...{len(alltweets)} tweets downloaded so far")

        cleaned_text = [re.sub(r'http[s]?:\/\/.*[\W]*', '', i.full_text, flags=re.MULTILINE) for i in alltweets] # remove urls
        cleaned_text = [re.sub(r'@[\w]*', '', i, flags=re.MULTILINE) for i in cleaned_text] # remove the @twitter mentions
        cleaned_text = [re.sub(r'RT.*','', i, flags=re.MULTILINE) for i in cleaned_text] # delete the retweets

    #transform the tweepy tweets array to fill the csv file
    outtweets = [[tweet.id_str, tweet.created_at, cleaned_text[idx].lower().replace('\n', ' '), len(tweet.full_text.lower()), tweet.source, tweet.retweet_count, tweet.favorite_count, round(TextBlob(tweet.full_text.lower()).sentiment.polarity,4)] for idx,tweet in enumerate(alltweets)]

    #write the csv
    with open(f'{screen_name}_tweets.csv', 'w', encoding='utf-8',  newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id","created_at","text", "length", "source", "retweets", "likes", "sentiment"])
        writer.writerows(outtweets)

    pass

### Main Funnction: Loop over twitter handle List in .txt file
### name of companies should be provided in firmhandles.txt
if __name__ == '__main__':
    filepath = 'firmhandles.txt'
    file = open(filepath, "r")
    for this_handle in file:
        try:
            print(this_handle.strip())
            get_all_tweets(this_handle.strip())
        except Exception:
            continue
