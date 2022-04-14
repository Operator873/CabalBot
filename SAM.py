import requests
import sqlite3
import re
from requests_oauthlib import OAuth1
from time import time
from sopel import plugin

SAM_DB = "/path/to/cabal.db"
NOT_AUTH = "You are not authorized to use the SAM module. Please contact the bot owner."
NO_TOKEN = (
        "Your OAuth is missing or has expired. "
        + "Please visit https://cabalbot.toolforge.org to login."
)

SAM_TOKEN = ""
SAM_SECRET = ""

def setup(bot):
    global SAM_TOKEN, SAM_SECRET
    db = sqlite3.connect(SAM_DB)
    c = db.cursor()

    try:
        SAM_TOKEN = c.execute("""SELECT data FROM config WHERE key="token";""").fetchone()[0]
        SAM_SECRET = c.execute("""SELECT data FROM config WHERE key="secret";""").fetchone()[0]
    except TypeError:
        bot.say(
            "Unable to find OAuth consumer information in database. "
            + "Loading SAM module has failed.",
            bot.config.core.owner
        )
    except IndexError:
        bot.say(
            "Missing key value in config table.",
            bot.config.core.owner
        )
    finally:
        db.close()


def xmit(api, data, action):
    headers = {
        "User-Agent": "CabalBot SAM Sopel plugin by Operator873",
        "From": "operator873@873gear.com"
    }

    key1, key2 = data["creds"]
    AUTH = OAuth1(SAM_TOKEN, SAM_SECRET, key1, key2)

    if action == "post":
        r = requests.post(api, headers=headers, data=data["payload"], auth=AUTH)
    elif action == "authget":
        r = requests.get(api, headers=headers, params=data["payload"], auth=AUTH)
    else:
        r = requests.get(api, headers=headers, params=data["payload"])

    return r.json()


def get_wp_account(user):  # Gatekeeper function
    db = sqlite3.connect(SAM_DB)
    c = db.cursor()

    try:
        account = c.execute("""SELECT wmf_account FROM sam_users WHERE irc_account=?;""", (user,)).fetchone()[0]
        response = {
            "status": True,
            "data": account
        }
    except TypeError:
        response = {
            "status": False,
            "data": NOT_AUTH
        }
    finally:
        db.close()

    return response


def get_creds(account):  # Assumes get_wp_account() has already found a match, but evaluates token age
    response = {
        "status": False
    }
    min_age = time() - 86400

    db = sqlite3.connect(SAM_DB)
    c = db.cursor()

    try:
        account, token, secret, timestamp = c.execute("""SELECT * FROM auth WHERE account=?;""", (account,)).fetchone()
    except TypeError:
        response["msg"] = "Unknown error occurred during processing of OAuth credentials."
        db.close()
        return response

    if (
        min_age > timestamp
        or token == ""
        or secret == ""
    ):
        c.execute("""DELETE FROM auth WHERE account=?;""", (account,))
        db.commit()
        response["msg"] = NO_TOKEN
    else:
        response["status"] = True
        response["creds"] = (token, secret)

    db.close()
    return response


def process_response(data):  # Process the response for most blocks
    block = data["block"]

    if 'error' in block:
        reason = block['error']['code']
        if reason == "badtoken":
            response = "Received CSRF token error. Try again..."
        elif reason == "alreadyblocked":
            response = data["target"] + " is already blocked. Use !reblock to change the current block."
        elif reason == "permissiondenied":
            response = "Received permission denied error. Are you a sysop on " + data["project"] + "?"
        elif reason == "invalidexpiry":
            response = (
                "The expiration time isn't valid. "
                + "I understand things like 31hours, 1week, 6months, infinite, indefinite."
            )
        else:
            info = block['error']['info']
            code = block['error']['code']
            response = "Unhandled error: " + code + " " + info
    elif 'block' in block:
        user = block['block']['user']
        expiry = block['block']['expiry']
        reason = block['block']['reason']
        response = user + " was blocked until " + expiry + " with reason: " + reason
    else:
        response = "Unknown error: " + block

    return response


def get_wiki(project):  # Fetches the apiurl for a project (ex: enwiki)
    db = sqlite3.connect(SAM_DB)
    c = db.cursor()

    site = c.execute('''SELECT apiurl FROM wikis WHERE wiki=?;''', (project,)).fetchone()

    db.close()

    if site is None:
        return None
    else:
        return site[0]


def get_api_token(site, creds, tkn_type):
    # Conducts the initial transaction to obtain the appropriate token for the user
    response = {
        "status": False,
        "msg": ""
    }
    reqtoken = {
        'action': "query",
        'meta': "tokens",
        'format': "json",
        'type': tkn_type
    }

    data = {
        "creds": creds,
        "payload": reqtoken
    }

    token = xmit(site, data, "authget")

    # Check for errors and return csrf
    if 'error' in token:
        response["msg"] = token['error']['info']
    else:
        response = {
            "status": True,
            "msg": token['query']['tokens']['%stoken' % tkn_type]
        }

    return response


def do_block(user, params, reblock):
    # Blocks target: Allows TPA, prohibits account creation, autoblocks underlying IP
    # Standard default block
    # If reblock is True, adds "reblock" param to payload to override existing block
    site = get_wiki(params['p'])
    if site is None:
        response = "I don't know that wiki."
        return response

    user_identity = preflight_user(user, site)
    if not user_identity["status"]:
        return user_identity["msg"]

    request_block = {
        "action": "block",
        "user": params['a'],
        "expiry": params['d'],
        "reason": params['r'],
        "token": user_identity['csrf'],
        "allowusertalk": "",
        "nocreate": "",
        "autoblock": "",
        "format": "json"
    }

    if reblock:
        request_block["reblock"] = ""

    msg = {
        "creds": user_identity["creds"],
        "payload": request_block
    }

    # Send block request
    data = {
        "block": xmit(site, msg, "post"),
        "target": params['a'],
        "project": params['p']
    }

    return process_response(data)


def process_args(args):
    args = "a=" + args
    l = re.split(r"(\w+)=", args)[1:]

    data = {l[i]: l[i + 1] for i in range(0, len(l), 2)}

    for key in data:
        data[key] = data[key].strip()

    if 'd' in data:
        adjust = re.sub(r"([0-9]+([0-9]+)?)", r" \1 ", data['d'])
        data['d'] = re.sub(' +', ' ', adjust).strip()

    return data


def check_command(params, len):
    if 'd' in params:
        if params['d'] == "indef" or params['d'] == "forever":
            params['d'] = "never"

    if len(params) < len:
        return False
    elif params['a'] == '':
        return False
    else:
        return True


def preflight_user(user, site):
    result = {
        "status": True
    }

    creds = get_creds(user)
    if not creds["status"]:
        result = {
            "status": False,
            "msg": creds["msg"]
        }
    else:
        result["creds"] = creds["creds"]

    csrfToken = get_api_token(site, creds["creds"], "csrf")
    if csrfToken["status"] is False:
        result = {
            "status": False,
            "msg": csrfToken["msg"]
        }
    else:
        result["csrf"] = csrfToken["msg"]

    return result

@plugin.command('block')
@plugin.nickname_commands('block')
def command_block(bot, trigger):
    # !block Some Nick Here p=project d=duration r=reason
    params = process_args(trigger.group(2))
    user = get_wp_account(trigger.account)

    if not check_command(params, 4):
        bot.say(
            "Command is malformed. "
            + "Syntax is: !block <target account> p=project d=duration r=reason for block. "
            + "Target of block must go first or be indicated with 'a=<account or target of block>'. "
        )
        return
    elif not user["status"]:
        bot.say(user["data"])
        return
    else:
        bot.say(do_block(user["data"], params, False))


@plugin.command('reblock')
@plugin.nickname_commands('reblock')
def command_block(bot, trigger):
    # !block Some Nick Here p=project d=duration r=reason
    params = process_args(trigger.group(2))
    user = get_wp_account(trigger.account)

    if not check_command(params, 4):
        bot.say(
            "Command is malformed. "
            + "Syntax is: !reblock <target account> p=project d=duration r=reason for block. "
            + "Target of block must go first or be indicated with 'a=<account or target of block>'. "
        )
        return
    elif not user["status"]:
        bot.say(user["data"])
        return
    else:
        bot.say(do_block(user["data"], params, True))

