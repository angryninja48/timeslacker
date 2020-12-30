# Time Slacker

## Overview

Flask driven bot used to interact with Slack and a timesheet portal (no api) using selenium

![Yes No Button](./images/yes_no_button.png)

## Quick start

### Slack

- [Create a slack app](https://api.slack.com/apps?new_app=1). Enable Bots > Review Scopes to Add > Add and Oauth Scope > chat:write > Install to Workspace
- Copy the OAuth token and add the environment variables to be used in the .env file
- [Create a slash command](https://api.slack.com/apps) and set the url to a public https url
- [Set interactivity url](https://api.slack.com/apps) and set the request url to a public https url
- Write `/kickoff` to your new bot

### Environment Variables

Create an .env file with the following environment variables

```
cat << EOF > .env
TS_USER=user
TS_PASSWORD=password
SLACK_TOKEN=xoxb-xxxx-yyyy-zzzzz
TIME_SHEET_URL=https://example.net
EOF
```

### Bot

```
docker build -t timeslacker .
docker run --name timeslacker -p 8000:8000 --env-file=.env timeslacker
```

**NOTE**: The bot needs to have a publicly accessable url for slack to hit

