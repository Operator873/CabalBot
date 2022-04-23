import requests

import cabalutil


def send_alert(msg, priority):
    api_token = cabalutil.do_sqlite(
        "SELECT data FROM config WHERE key='cabalbot_pushover';",
        "one"
    )[0]

    group_token = cabalutil.do_sqlite(
        "SELECT data FROM config WHERE key='cabalbot_pushover_group';",
        "one"
    )[0]

    pushover = "https://api.pushover.net/1/messages.json"

    alert = {
        "token": api_token,
        "user": group_token,
        "title": "Bot873 Alert!",
        "message": msg,
        "priority": priority,
    }

    if priority == 2:
        alert["retry"] = 30
        alert["expire"] = 180

    response = requests.post(pushover, data=alert).json()

    if "status" in response and response["status"] == 1:
        return True
    else:
        return False
