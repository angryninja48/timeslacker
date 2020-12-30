import os
import json
import datetime

from flask import Flask
from app import TimeSheet

from slackify import (ACK, OK, Slackify, async_task, reply_text, block_reply,
                      request, respond, text_block, Slack)

TS_USER = os.getenv("TS_USER")
TS_PASSWORD = os.getenv("TS_PASSWORD")
SLACK_TOKEN = os.getenv("SLACK_TOKEN")

app = Flask(__name__)
slackify = Slackify(app=app)
cli = Slack(SLACK_TOKEN)

@slackify.command
def kickoff():
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
    text_blok = text_block(':rocket: Submitting timesheet...')
    respond(action['response_url'], {'blocks': [text_blok]})
    submit_timesheet()
    # user_id = action['user'].get('id')
    # text_blok = text_block(f':heavy_check_mark: Timesheet Submitted.\n')
    # send_message(cli, [text_blok], user_id)
    return OK


@slackify.action(action_id="no")
def no(action):
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

    submit_timesheet(days=working_days)

    # text_blok = text_block(f':heavy_check_mark: Timesheet Submitted.\n')
    # send_message(cli, [text_blok], payload_response['user']['id'])

@async_task
def submit_timesheet(days=None):
    time = TimeSheet(username=TS_USER,password=TS_PASSWORD,days=days)
    submit = time.run()
    date = datetime.datetime.now().strftime("%d-%m-%Y")
    cli.chat_postMessage(channel='#timesheets', text=f':white_check_mark: Timesheet Submitted - *{date}*')


@async_task
def send_message(cli, blocks, user_id):
    return cli.chat_postMessage(channel=user_id, user_id=user_id, blocks=blocks)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000,debug=True)
