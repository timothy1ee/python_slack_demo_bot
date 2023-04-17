# Slack Bot Starter

This project demonstrates how to get started with creating a simple Slack bot using the Slack Bolt Framework. The bot can respond to messages in direct messages (DMs), channels, and threads.

## Supported Use Cases

This demo Slack bot supports the following use cases:

- Respond to direct messages (DMs) with an echo of the received message.
- Respond to mentions in a channel with an echo of the received message.
- Respond to messages in threads where the bot was mentioned with an echo of the received message.

Of course, instead of simply echoing your message, you can determine what bot logic to use.

Some bot logic also requires the full thread history for context, so the demo code also illustrates how to maintain a hash of thread conversations.

## Installation

### Configuring the Slack App

1. Create a new Slack app at https://api.slack.com/apps
2. Navigate to the "OAuth & Permissions" page and add the following scopes:
   - `app_mentions:read` - To receive events when the bot is mentioned.
   - `chat:write` - To send messages as the bot.
   - `channels:history` - To fetch messages in public channels.
   - `groups:history` - To fetch messages in private channels.
   - `im:history` - To fetch messages in direct message channels.
   - `im:write` - To send messages in direct message channels.
   - `mpim:history` - To fetch messages in multi-person direct message channels.
   - `mpim:write` - To send messages in multi-person direct message channels.
   - `channels:join` - (Optional) To allow the bot to join channels automatically when invited.
3. Install the app to your workspace and copy the "Bot User OAuth Token" (SLACK_BOT_TOKEN) from the "OAuth & Permissions" page to the .env file.
4. Navigate to the "Event Subscriptions" page, enable events, and add the following event subscriptions:
   - `message.channels` - To receive messages posted in public channels.
   - `message.groups` - To receive messages posted in private channels.
   - `message.im` - To receive messages posted in direct message channels.
   - `message.mpim` - To receive messages posted in multi-person direct message channels.
   - `app_mention` - To receive events when the bot is mentioned.
6. In "Basic Information", copy the signing secret to the .env file.

## Installation

Make sure you have Python 3 installed on your development machine. If you don't have it, install Python 3 using your package manager or from the official website: https://www.python.org/downloads/

Create a virtual environment for your project. In the terminal, navigate to the project's root directory and run the following command:

```
python3 -m venv venv
```

This will create a new virtual environment named venv in your project directory.

Activate the virtual environment:

```bash
source venv/bin/activate
```

Install the required dependencies using pip. In the project directory, run:

```bash
pip install -r requirements.txt
```

This will install the packages listed in the requirements.txt file into the virtual environment.

## Running the Server

### Development

Install ngrok from https://ngrok.com/download and start it by running:

```bash
ngrok http 3000
```

Copy the HTTPS forwarding URL (e.g., https://xxxxxxxxxxxx.ngrok.io) and set it as the "Request URL" in the "Event Subscriptions" page of your Slack app configuration. Append /slack/events, e.g., https://xxxxxxxxxxxx.ngrok.io/slack/events

In the project directory, create a .env file with the following content:

```bash
SLACK_BOT_TOKEN=<your_slack_bot_token>
SLACK_SIGNING_SECRET=<your_slack_signing_secret>
```

Replace <your_slack_bot_token> and <your_slack_signing_secret> with the appropriate values from your Slack app configuration.

Start the development server by running:

```bash
python app.py
```

### Production

This section assumes you are using Ubuntu.

After activating the virtual environment, install Gunicorn, a Python WSGI HTTP server:

```
pip install gunicorn
```

Create a new file named gunicorn.conf.py in your project directory with the following content:

```python
workers = 4
bind = "0.0.0.0:3000"
module = "app:app"
```

Start the server with Gunicorn:

```bash
gunicorn -c gunicorn.conf.py
```

This will start the server in the background and automatically restart it if it crashes.

To ensure the server starts automatically when your system boots up, consider using a process manager like systemd to manage the Gunicorn process.

To set up the systemd service, create a new file named slackbot.service in /etc/systemd/system/ with the following content:

```makefile
[Unit]
Description=Slack Bot
After=network.target

[Service]
User=<your_username>
Group=<your_group>
WorkingDirectory=<path_to_your_project_directory>
Environment="PATH=<path_to_your_project_directory>/venv/bin"
ExecStart=<path_to_your_project_directory>/venv/bin/gunicorn -c gunicorn.conf.py

[Install]
WantedBy=multi-user.target
Replace <your_username>, <your_group>, and <path_to_your_project_directory> with the appropriate values. If you're using a virtual environment, make sure to update the PATH and ExecStart values accordingly.
```

After creating the slackbot.service file, run the following commands to enable and start the service:

```bash
sudo systemctl enable slackbot.service
sudo systemctl start slackbot.service
```

To check the status of the service, run:

```bash
sudo systemctl status slackbot.service
```

Now your Slack bot should be running in production with the Flask server managed by systemd.

On the Slack API dashboard, in the "Event Subscriptions", set the "Request URL" to the public IP address or hostname. Append /slack/events, e.g., https://23.44.33.45/slack/events