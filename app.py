import os
import os.path
import json
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient
from flask import Flask, request, make_response
import logging

load_dotenv()

app = Flask(__name__)
slack_app = App(token=os.environ["SLACK_BOT_TOKEN"])
handler = SlackRequestHandler(slack_app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
THREADS_FILE = os.path.join(BASE_DIR, "threads.json")
threads = {}

# app.logger.setLevel(logging.DEBUG)
app.logger.info("Server started")

@app.before_request
def log_request_info():
    app.logger.info(f'{request.method} {request.path} {request.remote_addr}')

@slack_app.event("app_mention")
@slack_app.event("message")
def handle_event(body, logger):
    app.logger.debug("Event received: %s", body)

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
    app.logger.debug("Handling incoming message: %s", event)

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

    with open(THREADS_FILE, "w") as f:
        json.dump(threads, f, indent=2)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

def load_threads():
    try:
        with open(THREADS_FILE, "r") as f:
            threads = json.load(f)
    except FileNotFoundError:
        threads = {}
    return threads

threads = load_threads()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 3000)), debug=True)
