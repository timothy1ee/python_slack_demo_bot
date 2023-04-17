import os
import json
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient
from flask import Flask, request, make_response

import logging

# Configure logging
log_file = "app.log"
logging.basicConfig(filename=log_file, level=logging.DEBUG)

load_dotenv()

app = Flask(__name__)
slack_app = App(token=os.environ["SLACK_BOT_TOKEN"])
handler = SlackRequestHandler(slack_app)
threads = {}

app.logger.info("Server started")

@slack_app.event("app_mention")
@slack_app.event("message")
def handle_event(body, logger):
    event = body["event"]

    if event.get("subtype") == "bot_message":
        return

    # Handle messages that are direct messages, mentions in a channel,
    # or subsequent messages in a thread that has mentioned the bot
    if (event.get("channel_type") == "im" 
        or event.get("type") == "app_mention"
        or threads.get(event.get("thread_ts"))):
        return handle_incoming_message(event)


def handle_incoming_message(event):
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    message = event["text"]
    thread_ts = event.get("thread_ts") or event["ts"]

    if not threads.get(thread_ts):
        result = client.conversations_replies(
            channel=event["channel"],
            ts=thread_ts,
        )
        threads[thread_ts] = result["messages"]
    else:
        threads[thread_ts].append(event)

    result = client.chat_postMessage(
        channel=event["channel"],
        text=f"You said: {message}",
        thread_ts=thread_ts,
    )
    threads[thread_ts].append(result["message"])

    with open("threads.json", "w") as f:
        json.dump(threads, f, indent=2)

    print([message["text"] for message in threads[thread_ts]])

@app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

def load_threads():
    try:
        with open("threads.json", "r") as f:
            threads = json.load(f)
    except FileNotFoundError:
        threads = {}
    return threads

if __name__ == "__main__":
    threads = load_threads()
    app.run(port=int(os.environ.get("PORT", 3000)))
