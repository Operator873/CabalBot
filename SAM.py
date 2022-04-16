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
LWCU = "https://login.wikimedia.org/w/api.php"
ANSWERS = ["true", "yes", "y"]
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
        min_age > float(timestamp)
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
        response = "I don't know " + params['p'] + "."
        return response

    user_identity = preflight_user(user, site, "csrf")
    if not user_identity["status"]:
        return user_identity["msg"]

    request_block = {
        "action": "block",
        "user": params['a'],
        "expiry": params['d'],
        "reason": params['r'],
        "token": user_identity['token'],
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


def do_soft_block(user, params):
    # Performs soft block
    site = get_wiki(params['p'])
    if site is None:
        response = "I don't know that wiki."
        return response

    user_identity = preflight_user(user, site, "csrf")
    if not user_identity["status"]:
        return user_identity["msg"]

    request_block = {
        "action": "block",
        "user": params['a'],
        "expiry": params['d'],
        "reason": params['r'],
        "token": user_identity['token'],
        "allowusertalk": "",
        "format": "json"
    }

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


def do_global_block(user, params, reblock):
    site = "https://meta.wikimedia.org/w/api.php"

    user_identity = preflight_user(user, site, "csrf")
    if not user_identity["status"]:
        return user_identity["msg"]

    block = {
        "action": "globalblock",
        "format": "json",
        "target": params['a'],
        "expiry": params['d'],
        "reason": params['r'],
        "alsolocal": True,
        "token": user_identity["token"]
    }

    if "anon" in params:
        if params['anon'] in ANSWERS:
            block["anononly"] = True
            block["localanononly"] = True

    if reblock:
        block["modify"] = True

    msg = {
        "creds": user_identity["creds"],
        "payload": block
    }

    # Send block request
    gblock = xmit(site, msg, "post")

    if 'error' in gblock:
        failure = gblock['error']['globalblock'][0]
        if failure['code'] == "globalblocking-block-alreadyblocked":
            response = params['a'] + " is already blocked."
        else:
            response = "Block failed! " + str(failure['message'])
    elif 'block' in gblock or 'globalblock' in gblock:
        expiry = gblock['globalblock']['expiry']
        if reblock:
            response = "Block was modified. New expiry: " + expiry
        elif block["anononly"]:
            response = "Anon-only block succeeded. Expiry: " + expiry
        else:
            response = "Block succeeded. Expiry: " + expiry
    else:
        response = "Unknown failure... " + gblock

    return response


def do_lock(user, params, action):
    site = "https://meta.wikimedia.org/w/api.php"
    user_identity = preflight_user(user, site, "setglobalaccountstatus")
    if not user_identity["status"]:
        return user_identity["msg"]

    lock = {
        "action": "setglobalaccountstatus",
        "format": "json",
        "user": params['a'],
        "locked": action,
        "reason": params['r'],
        "token": user_identity["token"]
    }

    msg = {
        "creds": user_identity["creds"],
        "payload": lock
    }

    # Send block request
    lock = xmit(site, msg, "post")

    if 'error' in lock:
        response = action + " action failed! " + lock['error']['info']
    else:
        response = params['a'] + " " + action + "ed."

    return response


def do_unblock(user, params):
    site = get_wiki(params['p'])
    if site is None:
        response = "I don't know that wiki."
        return response

    user_identity = preflight_user(user, site, "csrf")
    if not user_identity["status"]:
        return user_identity["msg"]

    unblock_payload = {
        "action": "unblock",
        "user": params["a"],
        "reason": params["r"],
        "token": user_identity["token"],
        "format": "json"
    }

    msg = {
        "creds": user_identity["creds"],
        "payload": unblock_payload
    }

    unblock = xmit(site, msg, "post")

    if 'error' in unblock:
        response = unblock['error']['info']
    elif 'unblock' in unblock:
        user = unblock['unblock']['user']
        reason = unblock['unblock']['reason']
        response = user + " was unblocked with reason: " + reason
    else:
        response = "Unhandled error: " + unblock

    return response


def process_args(args):
    args = "a=" + args
    l = re.split(r"(\w+)=", args)[1:]

    data = {l[i]: l[i + 1] for i in range(0, len(l), 2)}

    for key in data:
        data[key] = data[key].strip()

    if 'd' in data:
        adjust = re.sub(r"([0-9]+([0-9]+)?)", r" \1 ", data['d'])
        data['d'] = re.sub(' +', ' ', adjust).strip()
        if data['d'] == "indef" or data['d'] == "forever":
            data['d'] = "never"

    if 'r' in data:
        if data["r"].lower() == "proxy":
            data["r"] = "[[m:NOP|Open proxy]]: See the [[m:WM:OP/H|help page]] if you are affected"
        elif data["r"].lower() == "lta":
            data["r"] = "Long-term abuse"
        elif data["r"].lower() == "spam":
            data["r"] = "Spam-only account"
        elif data["r"].lower() == "spambot":
            data["r"] = "Spam-only account: spambot"
        elif data["r"].lower() == "abuse":
            data["r"] = "Cross-wiki abuse"
        elif data["r"] == "banned" or data["r"] == "banned user":
            data["r"] = "Globally banned user"

    data['a'] = data['a'].replace("_", " ")

    return data


def check_command(params, length):
    if len(params) < length:
        return False
    else:
        return True


def preflight_user(user, site, token):
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

    csrfToken = get_api_token(site, creds["creds"], token)
    if csrfToken["status"] is False:
        result = {
            "status": False,
            "msg": csrfToken["msg"]
        }
    else:
        result["token"] = csrfToken["msg"]

    return result


def sam_memory(user, payload, action):
    result = {
        "status": True
    }

    db = sqlite3.connect(SAM_DB)
    c = db.cursor()

    if action == "add":
        check = c.execute('''SELECT * FROM memory WHERE user=? AND payload=?;''', (user, payload)).fetchone()

        if check is None and payload is not None:
            try:
                c.execute('''INSERT INTO memory VALUES(?, ?);''', (user, payload))
                db.commit()
                result["data"] = "'" + payload + "' saved"
            except Exception as e:
                result["status"] = False
                result["data"] = str(e)
        elif payload is None:
            result['data'] = "Nothing to add. Try: .memadd <something here>"
        else:
            result['data'] = "'" + payload + "' is already in memory."

    elif action == "del":
        check = c.execute('''SELECT * FROM memory WHERE user=? AND payload=?;''', (user, payload)).fetchone()

        if check is not None:
            c.execute("""DELETE FROM memory WHERE user=? AND payload=?;""", (user, payload))
            db.commit()
            result['data'] = "'" + payload + "' removed from memory."
        else:
            result['status'] = False
            result['data'] = "'" + payload + "' is not currently in memory for " + user + "."

    elif action == "clear":
        try:
            c.execute("""DELETE FROM memory WHERE user=?;""", (user,))
            db.commit()
            result["data"] = "Memory cleared."
        except Exception as e:
            result["status"] = False
            result["data"] = str(e)

    elif action == "get":
        try:
            result['data'] = c.execute('''SELECT payload FROM memory WHERE user=?;''', (user,)).fetchall()
        except Exception as e:
            result['status'] = False
            result['data'] = str(e)

    db.close()
    return result


def do_lwcu_get_users(actor, target):
    result = {
        "status": False
    }

    query = {
        'action': "query",
        'list': "checkuser",
        'curequest': "ipusers",
        'cutarget': target,
        'cureason': "Checking proxy IP used by a spambot/LTA/xwiki vandal for additional accounts.",
        'cutoken': actor["token"],
        'cutimecond': "-3 months",
        'format': "json"
    }

    msg = {
        "creds": actor["creds"],
        "payload": query
    }

    data = xmit(LWCU, msg, 'post')

    if 'batchcomplete' in data:
        accounts = data['query']['checkuser']['ipusers']

        if len(accounts) > 1:
            result = {
                "status": True,
                "data": accounts
            }

    return result


def do_lwcu_get_IP(actor, target):
    result = {
        "status": False
    }

    query = {
        'action': "query",
        'list': "checkuser",
        'curequest': "userips",
        'cutarget': target,
        'cureason': "Checking spambot/LTA/xwiki vandal for proxy",
        'cutoken': actor["token"],
        'cutimecond': "-3 months",
        'format': "json"
    }

    msg = {
        "creds": actor["creds"],
        "payload": query
    }

    data = xmit(LWCU, msg, 'post')

    if 'batchcomplete' in data:
        result = {
            "status": True,
            "ips": data['query']['checkuser']['userips']
        }

    return result


def do_proxycheck(ip):
    ipurl = "https://ipcheck.toolforge.org/index.php"

    check = {
        'ip': ip,
        'api': "true",
        'key': "get_your_own_key"
    }

    result = requests.get(ipurl, check).json()

    try:
        proxy1 = result['ipQualityScore']['result']['proxy']
        proxy2 = result['proxycheck']['result']['proxy']
    except Exception as e:
        proxy1 = None
        proxy2 = None

    if proxy1 is True or proxy2 is True:
        return True
    else:
        return False


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
            + "Target of block must be first or be indicated with 'a=<account or target of block>'. "
        )
        return
    elif not user["status"]:
        bot.say(user["data"])
        return
    else:
        bot.say(do_block(user["data"], params, False))


@plugin.command('reblock')
@plugin.nickname_commands('reblock')
def command_reblock(bot, trigger):
    # !block Some Nick Here p=project d=duration r=reason
    params = process_args(trigger.group(2))
    user = get_wp_account(trigger.account)

    if not check_command(params, 4):
        bot.say(
            "Command is malformed. "
            + "Syntax is: !reblock <target account> p=project d=duration r=reason for block. "
            + "Target of block must be first or be indicated with 'a=<account or target of block>'. "
        )
        return
    elif not user["status"]:
        bot.say(user["data"])
        return
    else:
        bot.say(do_block(user["data"], params, True))

@plugin.command('gblock')
@plugin.nickname_command('gblock')
def global_block(bot, trigger):
    # !gblock SomeIP d=duration r=reason
    params = process_args(trigger.group(2))
    user = get_wp_account(trigger.account)

    if not check_command(params, 3):
        bot.say(
            "Command is malformed. "
            + "Syntax is: !gblock <target IP> d=duration r=reason for block. "
            + "Target of block must be first or be indicated with 'a=<account or target of block>'. "
        )
        return
    elif not user["status"]:
        bot.say(user["data"])
        return
    else:
        if 'reblock' in params:
            bot.say(do_global_block(user["data"], params, True))
        else:
            bot.say(do_global_block(user["data"], params, False))


@plugin.commands('lock')
@plugin.nickname_commands('lock')
def command_lock(bot, trigger):
    # !lock Some Account r=reason
    params = process_args(trigger.group(2))
    user = get_wp_account(trigger.account)

    if not check_command(params, 2):
        bot.say(
            "Command is malformed. "
            + "Syntax is: !lock <target account> r=reason for lock. "
            + "Target of lock must be first or be indicated with 'a=<target of lock>'. "
        )
        return
    elif not user["status"]:
        bot.say(user["data"])
        return
    else:
        bot.say(do_lock(user["data"], params, "lock"))

    if (
        params['r'] == "Spam-only account: spambot"
        or (
            'docu' in params
            and params['docu'] in ANSWERS
        )
    ):
        lwcu_identity = preflight_user(user["data"], LWCU, "csrf")
        target_ip = do_lwcu_get_IP(lwcu_identity, params['a'])

        if target_ip["status"]:
            for ip in target_ip["ips"]:
                if do_proxycheck(ip["address"]):
                    block_ip = {
                        'a': ip["address"],
                        'd': "3months",
                        'r': "[[m:NOP|Open proxy]]: See the [[m:WM:OP/H|help page]] if you are affected",
                    }
                    bot.say(do_global_block(user["data"], block_ip, False))

                find_accounts = do_lwcu_get_users(lwcu_identity, ip["address"])
                if find_accounts["status"]:
                    bot.say(
                        "LWCU found accounts "
                        + "https://login.wikimedia.org/w/index.php?title=Special:CheckUser&reason="
                        + params["r"]
                        + "&user="
                        + ip["address"]
                    )


@plugin.commands('unlock')
@plugin.nickname_commands('unlock')
def command_unlock(bot, trigger):
    # !unlock Some Account r=reason
    params = process_args(trigger.group(2))
    user = get_wp_account(trigger.account)

    if not check_command(params, 2):
        bot.say(
            "Command is malformed. "
            + "Syntax is: !unlock <target account> r=reason for unlock. "
            + "Target of unlock must be first or be indicated with 'a=<target of unlock>'. "
        )
        return
    elif not user["status"]:
        bot.say(user["data"])
        return
    else:
        bot.say(do_lock(user["data"], params, "unlock"))


@plugin.command('softblock')
@plugin.nickname_commands('softblock')
def command_softblock(bot, trigger):
    # !softblock Some Nick Here p=project d=duration r=reason
    params = process_args(trigger.group(2))
    user = get_wp_account(trigger.account)

    if not check_command(params, 4):
        bot.say(
            "Command is malformed. "
            + "Syntax is: !softblock <target account> p=project d=duration r=reason for block. "
            + "Target of block must be first or be indicated with 'a=<account or target of block>'. "
        )
        return
    elif not user["status"]:
        bot.say(user["data"])
        return
    else:
        bot.say(do_soft_block(user["data"], params))


@plugin.require_owner(message="This function is only available to the bot owner.")
@plugin.command('addsamuser')
@plugin.nickname_command('addsamuser')
def add_user(bot, trigger):
    # !addsamuser IRCaccount Wikipedia account with spaces

    try:
        irc, account = trigger.group(2).split(' ', 1)
    except ValueError:
        bot.say("Command is malformed! Syntax is !addsamuser <IRCaccount> <Wikipedia account>")
        return

    db = sqlite3.connect(SAM_DB)
    c = db.cursor()

    check = c.execute("""SELECT wmf_account FROM sam_users WHERE irc_account=?;""", (irc,)).fetchone()

    if check is None:
        c.execute("""INSERT INTO sam_users VALUES(?, ?);""", (irc, account.replace('_', ' ')))
        db.commit()
        bot.say(irc + " was granted access to the SAM plugin as Wikipedia account: " + account.replace('_', ' ') + ".")
    else:
        bot.say(irc + " already has access as " + check[0] + ".")

    db.close()



@plugin.require_owner(message="This function is only available to the bot owner.")
@plugin.command('delsamuser')
@plugin.nickname_command('delsamuser')
def del_user(bot, trigger):
    # !delsamuser Their WP Account or IRC account
    db = sqlite3.connect(SAM_DB)
    c = db.cursor()

    check = c.execute(
        """SELECT wmf_account FROM sam_users WHERE irc_account=? OR wmf_account=?;""",
        (trigger.group(2), trigger.group(2).replace('_', ' '))
    ).fetchone()

    if check is None:
        bot.say(trigger.group(2) + " was not found in the SAM users list.")
    else:
        c.execute("""DELETE FROM sam_users WHERE wmf_account=?;""", (check[0],))
        db.commit()
        bot.say("User with Wikipedia account: " + check[0] + " was deleted from SAM users.")

    db.close()


@plugin.command('memadd')
@plugin.nickname_commands('memadd')
def memadd(bot, trigger):
    result = sam_memory(trigger.account, trigger.group(2), "add")

    if result['status']:
        bot.say(result['data'])
    else:
        bot.say("Error! " + result['data'])


@plugin.command('memclear')
@plugin.nickname_commands('memclear')
def memclear(bot, trigger):
    result = sam_memory(trigger.account, None, "clear")

    if result['status']:
        bot.say(result['data'])
    else:
        bot.say("Error! " + result['data'])


@plugin.command('memdel')
@plugin.nickname_commands('memdel')
def memdel(bot, trigger):
    result = sam_memory(trigger.account, trigger.group(2), "del")

    if result['status']:
        bot.say(result['data'])
    else:
        bot.say("Error! " + result['data'])


@plugin.command('memshow')
@plugin.nickname_command('memshow')
def memshow(bot, trigger):
    payload = sam_memory(trigger.account, None, "get")

    if payload['status']:
        if len(payload['data']) > 0:
            response = ""
            for entry in payload['data']:
                if len(response) > 0:
                    response = response + ", " + entry[0]
                else:
                    response = entry[0]
            bot.say("Items currently in memory: " + response)
        else:
            bot.say("It doesn't appear you have anything stored in memory.")
    else:
        bot.say("An error occurred fetching memory items. -->" + payload['data'])


@plugin.command('memory')
@plugin.nickname_command('memory')
def memory(bot, trigger):
    try:
        action, info = trigger.group(2).split(" ", 1)
    except:
        bot.say("Missing data. Syntax is !memory <action> <optional args>")
        return

    user = get_wp_account(trigger.account)
    dump = sam_memory(trigger.account, None, "get")
    params = process_args(info)
    action = action.lower()

    if len(dump['data']) == 0:
        bot.say("There are no items in memory for you.")
        return

    if action == "lock":
        # !lock Some Account r=reason

        if not check_command(params, 2):
            bot.say(
                "Command is malformed. "
                + "Syntax is: !memory lock r=reason for unlock. "
            )
            bot.say("Memory items still intact.")
            return

        if not user["status"]:
            bot.say(user["data"])
            return

        for item in dump["data"]:
            params['a'] = item[0]
            do_lock(user, params, "lock")
            if (
                    params['r'] == "Spam-only account: spambot"
                    or (
                    'docu' in params
                    and params['docu'] in ANSWERS
            )
            ):
                lwcu_identity = preflight_user(user["data"], LWCU, "csrf")
                target_ip = do_lwcu_get_IP(lwcu_identity, params['a'])

                if target_ip["status"]:
                    for ip in target_ip["ips"]:
                        if do_proxycheck(ip["address"]):
                            block_ip = {
                                'a': ip["address"],
                                'd': "3months",
                                'r': "[[m:NOP|Open proxy]]: See the [[m:WM:OP/H|help page]] if you are affected",
                            }
                            bot.say(do_global_block(user["data"], block_ip, False))

                        find_accounts = do_lwcu_get_users(lwcu_identity, ip["address"])
                        if find_accounts["status"]:
                            bot.say(
                                "LWCU found accounts "
                                + "https://login.wikimedia.org/w/index.php?title=Special:CheckUser&reason="
                                + params["r"]
                                + "&user="
                                + ip["address"]
                            )
        sam_memory(user["data"], None, "clear")

    elif action == "block":
        if not check_command(params, 4):
            bot.say(
                "Command is malformed. "
                + "Syntax is: !memory block p=project d=duration r=reason for unlock. "
            )
            bot.say("Memory items still intact.")
            return
        elif not user["status"]:
            bot.say(user["data"])
            return
        else:
            for item in dump["data"]:
                params["a"] = item[0]
                do_block(user["data"], params, False)

            sam_memory(user['data'], None, "clear")

    elif action == "gblock":
        if not check_command(params, 3):
            bot.say(
                "Command is malformed. "
                + "Syntax is: Syntax is !memory gblock d=duration r=reason. "
            )
            bot.say("Memory items still intact.")
            return
        elif not user["status"]:
            bot.say(user["data"])
            return
        else:
            for item in dump["data"]:
                params['a'] = item[0]
                if 'reblock' in params:
                    bot.say(do_global_block(user["data"], params, True))
                else:
                    bot.say(do_global_block(user["data"], params, False))
            sam_memory(user['data'], None, "clear")

    elif action == "test":
        if not check_command(params, 2):
            bot.say(
                "Command is malformed. "
                + "Syntax is: !memory test r=Test reason. "
            )
            bot.say("Memory items still intact.")
            return
        elif not user["status"]:
            bot.say(user["data"])
            return
        else:
            for item in dump["data"]:
                params['a'] = item[0]
                bot.say(str(params))
    else:
        bot.say("I don't know the command: " + action)
        bot.say("Try something like lock, block, gblock, unblock, or cu")

