import argparse
import os
import json
from openai import OpenAI
from datetime import datetime, timezone
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import shelve


# OpenAI API
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
# Slack API
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
SLACK_TOKEN = os.getenv('SLACK_TOKEN')
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')

app = App(token=SLACK_BOT_TOKEN)

def save_channel_preferences(user_id, channel_ids):
    """Save user's channel preferences to a shelve database."""
    with shelve.open('channel_prefs.db') as db:
        db[user_id] = channel_ids

def get_channel_preferences(user_id):
    """Retrieve a user's channel preferences from the shelve database."""
    with shelve.open('channel_prefs.db') as db:
        return db.get(user_id, [])

@app.command("/digest")
def handle_digest(ack, say, command):
    # Acknowledge the command request
    ack()
    user_id = command['user_id']
    print(user_id) 
    channel_names = command['text'].split()
    channel_ids = [get_channel_id(name) for name in channel_names if get_channel_id(name)]

    if channel_ids:
        # Save channel preferences if new channels are provided
        save_channel_preferences(user_id, channel_ids)
        summaries = summarize_channels(user_id)
        if summaries:
            say(summaries)
        else:
            say("No new messages to summarize.")
    else:
        say("Could not find specified channels.")


def get_channel_id(channel_name):
    """ Retrieve the channel ID for a given channel name from Slack. """
    try:
        response = app.client.conversations_list()
        channels = response['channels']  # Access the list of channels
        for channel in channels:
            if channel['name'] == channel_name:
                return channel['id']
    except Exception as e:
        print(f"Error fetching channel list: {e}")
    return None

def summarize_channels(user_id):
    """ Fetch messages from the channels and summarize them using OpenAI. """
    channel_ids = get_channel_preferences(user_id)
    summaries = []
    utc_now = datetime.now(timezone.utc)
    start_of_today_utc = utc_now.replace(hour=0, minute=0, second=0, microsecond=0)

    for channel_id in channel_ids:
        try:
            result = app.client.conversations_history(
                channel=channel_id, 
                oldest=str(start_of_today_utc.timestamp()))
            messages = " ".join(msg['text'] for msg in result['messages'] if 'subtype' not in msg)
            if messages:
                response = client.chat.completions.create(model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Summarize the conversation."},
                          {"role": "user", "content": messages}],
                max_tokens=150)
                summary = response.choices[0].message.content.strip()
                summaries.append(f"Summary for <#{channel_id}>: {summary}")
        except SlackApiError as e:
            print(f"Error retrieving messages for channel {channel_id}: {e}")
    return "\n".join(summaries)

def main():
    parser = argparse.ArgumentParser(description='Run Slack bot and/or summarization.')
    parser.add_argument('--summarize-only', action='store_true', help='Run summarize_channels function only')
    args = parser.parse_args()

    if args.summarize_only:
        user_id = os.getenv('SUMMARIZE_USER_ID') 
        summarize_channels(user_id)
    else:
        SocketModeHandler(app, SLACK_TOKEN).start()

if __name__ == "__main__":
    main()

