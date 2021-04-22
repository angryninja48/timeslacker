import os
import json
import datetime
import hashlib
import hmac


from flask import Flask
from app import TimeSheet

from slackify import (ACK, OK, Slackify, async_task, reply_text, block_reply,
                      request, respond, text_block, Slack)

TS_USER = os.getenv("TS_USER")
TS_PASSWORD = os.getenv("TS_PASSWORD")
SLACK_TOKEN = os.getenv("SLACK_TOKEN")

DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}

app = Flask(__name__)
slackify = Slackify(app=app)
cli = Slack(SLACK_TOKEN)


def verify_slack(request):
    timestamp = request.headers['X-Slack-Request-Timestamp']
    slack_signature = request.headers['X-Slack-Signature']
    # request_body = request.get_data()
    slack_signing_secret = os.environ['SLACK_SIGNING_SECRET'].encode('utf8')

    # https://stackoverflow.com/questions/62878160/how-to-get-raw-request-payload-in-flask-connexion
    # Stupid hack - Guessing slackify encodes which returns get_data() empty
    import urllib.parse
    form_data = request.form
    request_body = '&'.join([k + '=' + urllib.parse.quote_plus(v) for k, v in form_data.items()])

    sig_basestring = f"v0:{timestamp}:{request_body}".encode('utf-8')
    my_signature = 'v0=' + hmac.new(slack_signing_secret, sig_basestring, hashlib.sha256).hexdigest()

    if hmac.compare_digest(my_signature, slack_signature):
        return True
    else:
        return False

@app.route('/kickoff')
def index():
    yes_no()
    return OK

@slackify.command
def yes_no():
    YES = 'yes'
    NO = 'no'
    yes_no_buttons = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Yes"
                },
                "style": "primary",
                "value": "normal_week",
                "action_id": YES
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "No"
                },
                "style": "danger",
                "value": "irregular_week",
                "action_id": NO
            }
        ]
    }
    blocks = [
        text_block('Did you do a normal working week?'),
        yes_no_buttons
    ]
    cli.chat_postMessage(channel='#timesheets', blocks=blocks)
    return OK

@slackify.action(action_id="yes")
def yes(action):

    if verify_slack(request):
        text_blok = text_block(':rocket: Submitting timesheet...')
        respond(action['response_url'], {'blocks': [text_blok]})
        submit_timesheet()
        return OK


@slackify.action(action_id="no")
def no(action):
    if verify_slack(request):
        response = json.loads(request.form["payload"])

        check_block = {
        	"type": "input",
        	"element": {
        		"type": "checkboxes",
                "action_id": "checkboxes-action",
        			"options": [
        				{
        					"text": {
        						"type": "plain_text",
        						"text": "Monday",
        						"emoji": True
        					},
        					"value": "Monday"
        				},
        				{
        					"text": {
        						"type": "plain_text",
        						"text": "Tuesday",
        						"emoji": True
        					},
        					"value": "Tuesday"
        				},
        				{
        					"text": {
        						"type": "plain_text",
        						"text": "Wednesday",
        						"emoji": True
        					},
        					"value": "Wednesday"
        				},
        				{
        					"text": {
        						"type": "plain_text",
        						"text": "Thursday",
        						"emoji": True
        					},
        					"value": "Thursday"
        				},
        				{
        					"text": {
        						"type": "plain_text",
        						"text": "Friday",
        						"emoji": True
        					},
        					"value": "Friday"
        				},
        				{
        					"text": {
        						"type": "plain_text",
        						"text": "Saturday",
        						"emoji": True
        					},
        					"value": "Saturday"
        				},
        				{
        					"text": {
        						"type": "plain_text",
        						"text": "Sunday",
        						"emoji": True
        					},
        					"value": "Sunday"
        				},
                    ]
            },
            "label": {
        		"type": "plain_text",
        		"text": "Please select working days",
        		"emoji": True
        	}
        }

        modal_blocks = [
            check_block
        ]
        workday_form = {
            "type": "modal",
            "callback_id": "workday_form",
            "title": {
                "type": "plain_text",
                "text": "Working Days",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
                "emoji": True
            },
            "blocks": modal_blocks
        }
        cli.views_open(
            trigger_id=response['trigger_id'],
            view=workday_form
        )
        text_blok = text_block(':rocket: Submitting timesheet...')
        respond(action['response_url'], {'blocks': [text_blok]})
        return OK

@slackify.view(view_callback_id="workday_form")
def register_callback():
    if verify_slack(request):
        process_payload(request.form["payload"])
        return OK

@async_task
def process_payload(payload):
    payload_response = json.loads(payload)
    block_id = payload_response["view"]["blocks"][0].get('block_id', None)
    action_id = payload_response["view"]["blocks"][0]["element"]["action_id"]
    reponse_values = payload_response["view"]["state"]["values"][block_id][action_id]["selected_options"]

    # Grab values and make a list
    working_days = []
    for i in reponse_values:
        working_days.append(i.get('value', None))

    # Get list of unworked days
    non_worked_days = list(set(working_days) - DAYS)

    submit_timesheet(days=working_days, non_worked_days=non_worked_days)


@async_task
def submit_timesheet(days=None, non_worked_days=None):
    time = TimeSheet(username=TS_USER,password=TS_PASSWORD,days=days, non_worked_days=non_worked_days)
    submit = time.run()
    date = datetime.datetime.now().strftime("%d-%m-%Y")
    cli.chat_postMessage(channel='#timesheets', text=f':white_check_mark: Timesheet Submitted - *{date}*')


@async_task
def send_message(cli, blocks, user_id):
    return cli.chat_postMessage(channel=user_id, user_id=user_id, blocks=blocks)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000,debug=True)
