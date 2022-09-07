import requests
import cabalutil


def send_alert(msg, bot):
    get_api_token = "SELECT data FROM config WHERE key='{}_pushover';".format(bot.lower())
    get_group_token = "SELECT data FROM config WHERE key='{}_pushover_group';".format(bot.lower())
    pushover = "https://api.pushover.net/1/messages.json"

    api_token = cabalutil.do_sqlite(get_api_token, "one")[0]
    group_token = cabalutil.do_sqlite(get_group_token, "one")[0]

    alert = {
        "token": api_token,
        "user": group_token,
        "title": "{} Alert!".format(bot),
        "message": msg['data'],
        "priority": msg['priority']
    }

    if msg['priority'] == 2:
        alert["retry"] = 30
        alert["expire"] = 180

    response = requests.post(pushover, data=alert).json()

    if "status" in response and response["status"] == 1:
        return True
    else:
        return False
