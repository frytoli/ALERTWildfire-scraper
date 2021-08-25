#!/usr/bin/python3

from searchtweets import load_credentials, gen_request_parameters, collect_results
import time
import db

def main():
    # Initialize db object
    adb = db.arangodb()
    # Query tweets every 10 minutes
    while True:
        # Load credentials from environment vars
        search_args = load_credentials(None)
        # Craft query
        query = gen_request_parameters('@alertwildfire', granularity=None, results_per_call=10)
        # Collect tweet results
        tweets = collect_results(query, max_tweets=10, result_stream_args=search_args)[0]['data']
        # Sort tweets by id (larger id is more recent)
        tweets = sorted(tweets, key=lambda k: k['id'], reverse=True)
        # Write to database
        for tweet in tweets:
            adb.insert_new_tweet(tweet['id'], tweet['text'])
        # Try again in 1 hour
        time.sleep(3600)

if __name__ == '__main__':
    main()
