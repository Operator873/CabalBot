import cabalutil
import sqlite3
import requests

def make_request(api, payload, post=False):
    headers = {
        "User-Agent": "CabalBot v2.0 by Operator873",
        "From": "operator873@gmail.com"
    }
    if post:
        r = requests.post(api, data=payload, headers=headers)
    else:
        r = requests.get(api, params=payload, headers=headers)
    tmp = r.json()
    error_code = tmp.get('error', {}).get('code', None)
    if error_code == 'mwoauth-invalid-authorization':
        print('Received auth error. Halting API attempt.')
        return False
    elif error_code is not None:
        print('ERROR: Received error code %s' % error_code)
        return False
    else:
        return r

def check(change):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    confirmed_exists = c.execute(
        """SELECT * FROM confirmed_feed WHERE project=?;""", (change["wiki"],)
    ).fetchall()

    db.close()

    if len(confirmed_exists) > 0:
        PROJ_API = change["server_url"] + "/w/api.php"
        editor = change["user"]
        r = make_request(PROJ_API, {
            "action": "query",
            "format": "json",
            "list": "users",
            "usprop": "rights",
            "ususers": editor
        })

        if not r:
            return False

        try:
            rights = r.json()["query"]["users"][0]["rights"]
        except KeyError:
            return False

        if "autoconfirmed" not in rights:
            return True
        else:
            return False
    else:
        return False


def report(bot, change):
    proj = change["wiki"]
    report = None
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    channel = c.execute(
        """SELECT channel FROM confirmed_feed WHERE project=?;""", (proj,)
    ).fetchall()

    if len(channel) > 0:
        if change["type"] == "log":
            no_action = [
                "ABUSEFILTER",
                "BLOCK",
                "DELETE",
                "IMPORT",
                "MASSMESSAGE",
                "NEWUSERS",
                "PAGETRANSLATION",
                "PATROL",
                "PROTECT",
                "RENAMEUSER",
                "REVIEW",
                "RIGHTS",
                "THANKS",
            ]

            action = str(change["log_type"]).upper()
            subType = str(change["log_action"]).upper()
            pageLink = change["meta"]["uri"]
            space = "\u200B"
            editor = change["user"][:2] + space + change["user"][2:]
            comment = str(change["comment"]).replace("\n", "")

            if action in no_action:
                return
            elif action == "MOVE":
                report = (
                    "Log action: "
                    + action
                    + " || New user "
                    + editor
                    + " moved "
                    + pageLink
                    + " "
                    + comment[:200]
                )
            else:
                report = (
                    "Log action: "
                    + action
                    + " || New user "
                    + editor
                    + " "
                    + pageLink
                    + " "
                    + comment[:200]
                )

        elif change["type"] == "edit" or change["type"] == "new":
            title = str(change["title"])
            chRev = str(change["revision"]["new"])
            chURL = change["server_url"]
            chDiff = chURL + "/w/index.php?diff=" + chRev
            chComment = change["comment"]
            editor = change["user"]
            space = "\u200B"
            editor = editor[:2] + space + editor[2:]

            if change["type"] == "edit":
                report = (
                    "\x02"
                    + title
                    + "\x02 was edited by new user \x02"
                    + editor
                    + "\x02 "
                    + chDiff
                    + " "
                    + chComment
                )
            elif change["type"] == "new":
                report = (
                    "\x02"
                    + title
                    + "\x02 was created by new user \x02"
                    + editor
                    + "\x02 "
                    + chDiff
                    + " "
                    + chComment
                )

        if report is not None:
            for chan in channel:
                if cabalutil.check_hush(chan[0]) is True:
                    continue
                else:
                    bot.say(report, chan[0])


def checkchannel(project, channel):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    check = c.execute(
        """SELECT channel FROM confirmed_feed WHERE project=? and channel=?;""",
        (project, channel),
    ).fetchall()

    db.close()

    if len(check) > 0:
        return True
    else:
        return False


def add_channel(project, channel):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    try:
        c.execute("""INSERT INTO confirmed_feed VALUES(?, ?);""", (project, channel))
        db.commit()
        result = True
    except Exception as e:
        result = False
    finally:
        db.close()
        return result


def del_channel(project, channel):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    try:
        c.execute(
            """DELETE FROM confirmed_feed WHERE project=? and channel=?;""", (project, channel)
        )
        db.commit()
        result = True
    except Exception as e:
        result = False
    finally:
        db.close()
        return result


def start(trigger):
    if not cabalutil.check_feedadmin(trigger.account, trigger.sender):
        response = (
            "You are not authorized to start the Not Confirmed feed in this channel."
        )
        return response

    if checkchannel(trigger.group(3), trigger.sender):
        response = (
            "I'm already reporting Not Confirmed actions for "
            + trigger.group(3)
            + " in this channel."
        )
        return response

    if add_channel(trigger.group(3), trigger.sender):
        response = (
            "I will report Not Confirmed actions on " + trigger.group(3) + " in this channel."
        )
    else:
        response = "An unknown error occurred during addition to database."

    return response


def stop(trigger):
    if not cabalutil.check_feedadmin(trigger.account, trigger.sender):
        response = (
            "You are not authorized to stop the Not Confirmed feed in this channel."
        )
        return response

    if not checkchannel(trigger.group(3), trigger.sender):
        response = "I'm not reporting Not Confirmed actions in this channel."
        return response

    if del_channel(trigger.group(3), trigger.sender):
        response = "Not Confirmed actions for " + trigger.group(3) + " have been stopped."
    else:
        response = "An unknown error occurred during removal from the database."

    return response
