import requests
import tweepy
import re

import config

LAST_TWEET_FILENAME = 'last_tweet'

LABELS = {
  'alert': '⚠',
  'police_presence': '👮',
  'units_requested': '🚓',
  'fire': '🔥',
  'prisoner_van': '🚐',
  'group': '🚩',
  'injury': '🩹',
  'barricade': '🚧',
  'aviation': '🚁',
  'other': '🔹'
}

# Tweet can be 280 characters, but this leaves some extra room for emoji,
# which count as two characters
MAX_TWEET_LENGTH = 270


def setup_api():
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

    return tweepy.API(auth)


# Read the timestamp of the last log item tweeted from a file
# Returns None if not found
def get_last_timestamp():
    last_log_tweeted = None

    try:
        with open(LAST_TWEET_FILENAME, 'r') as f:
            last_log_tweeted = float(f.read())
    except FileNotFoundError:
        pass
    except Exception as e:
        # Treat any kind of error as if we haven't tweeted before
        print(e)

    return last_log_tweeted


# Write the given timestamp to a file for reading on the next execution
def save_last_timestamp(timestamp):
    print(f'Updating last tweet file with timestamp {timestamp}')
    with open(LAST_TWEET_FILENAME, 'w') as f:
        f.write(timestamp)


# Render a log item to a tweetable string
def format_tweet(data):
    emoji = LABELS.get(data['label'], '')
    label = data['label'].replace('_', ' ').capitalize() if data['label'] != 'other' else ''

    return f"{emoji + ' ' if emoji else ''}{label + ' at ' if label else ''}{data['location']}\n{data['text']}"


# Tweet a log item and return the timestamp
# If the formatted tweet is too long for a single tweet, item is broken into
# a thread.
def tweet_log_item(api, log):
    tweet = format_tweet(log['data'])

    if len(tweet) < MAX_TWEET_LENGTH:
        print(tweet)
        api.update_status(tweet)
    else:
        # Chunk string into tweets
        tweets = re.findall(f".{{1,{MAX_TWEET_LENGTH}}}", tweet, flags=re.S)
        print("Splitting tweet...")
        # Tweet message as a thread
        id = None
        for tweet in tweets:
            print(tweet)
            print('')
            id = api.update_status(tweet, in_reply_to_status_id=id).id

    print('-----------------------')

    return log['timestamp']


# Tweet any log updates from scanmap since the last execution
def main():
    api = setup_api()

    response = requests.get(config.LOG_URL)
    parsed_response = response.json()
    logs = parsed_response['logs']

    last_log_tweeted = get_last_timestamp()
    if last_log_tweeted:
        latest_logs = [log for log in logs if float(log['timestamp']) > last_log_tweeted]
        print(f"{len(latest_logs)} new logs to tweet")
    else:
        print('Timestamp for last log tweeted not found. Tweeting most recent log line only')
        latest_logs = [logs[-1]]

    if len(latest_logs) == 0:
        exit(0)

    last_timestamp = None
    for log in latest_logs:
        try:
            last_timestamp = tweet_log_item(api, log)
        except tweepy.TweepError as e:
            # Continue on duplicate status error
            if e.api_code == 187:
                print("Duplicate status, continuing")
                last_timestamp = log['timestamp']
                continue
            else:
                print(e)
                break

    if last_timestamp:
        save_last_timestamp(last_timestamp)


main()
