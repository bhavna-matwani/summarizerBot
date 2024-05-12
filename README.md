# Slack Channel Summarizer

This Python script enables a Slack app to summarize messages from specified channels using OpenAI's GPT-3.5 model. It also includes functionality to respond to real-time Slack commands and can operate in a scheduled mode to run summarizations periodically.

## Features

- **Real-Time Interaction**: Responds to `/digest` command in Slack to summarize channel messages based on user preferences.
- **Batch Summarization**: Can be scheduled to automatically summarize messages from specified channels at regular intervals using a cron job or similar scheduling mechanism.
- **Customizable**: User and channel preferences can be stored and retrieved using a shelve database, allowing for persistent and customizable configurations.

## Prerequisites

Before you can run this script, you'll need:

- Python 3.8+
- Slack App with a Bot token and permissions to read channel messages and post messages.
- An OpenAI API key with access to the GPT-3.5 model.

## Setup

### Environment Variables

You need to set the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key.
- `SLACK_BOT_TOKEN`: Your Slack Bot User OAuth Token (`xoxb-`).
- `SLACK_TOKEN`: Your Slack App-Level Token (`xapp-` for Socket Mode).
- `SLACK_WEBHOOK_URL`: Your Slack incoming webhook URL (if needed).

You can set these variables in your environment or use a `.env` file and load them with `python-dotenv`.

### Installing Dependencies

Install the required Python packages:

```bash
pip install openai slack_bolt slack_sdk shelve
```

## Configuring the Slack App

1. **Create a new Slack App** in your workspace.
2. **Add the Bot Token Scopes**: 
   - `channels:history`
   - `chat:write`
   - `commands`
3. **Install the app** to your workspace and invite it to the channels it needs access to.

## Usage

### Running the App

- **Interactive Mode (listening to Slack events):**
  ```bash
  python slackgpt.py
  ```
- **Batch Mode (Daily Summaries):**
```bash
python slackgpt.py --summarize-only
```

## Slack Commands
```
/digest [channel_names]: Triggers the summarization of the specified channels and posts the summaries and stores it in the db for cron job.
```
