import sqlite3
import random
import requests
from requests_oauthlib import OAuth1


def getdb():
    return "/path/to/.sopel/plugins/cabal.db"


def do_sqlite(query, method):
    db = sqlite3.connect(getdb())
    c = db.cursor()

    if method == "all":
        data = c.execute(query).fetchall()
    elif method == "act":
        try:
            c.execute(query)
            db.commit()
            return True
        except Exception as e:
            print(str(e))
            return False
    else:
        data = c.execute(query).fetchone()

    db.close()

    return data


def get_creds():
    db = sqlite3.connect(getdb())
    c = db.cursor()

    creds = c.execute("""SELECT data FROM config WHERE key="creds";""").fetchone()

    db.close()

    return creds[0]


def xmit(url, payload, action="get"):
    prefix = "https://"
    suffix = "/w/api.php"
    api = prefix + url + suffix
    headers = {"User-Agent": "CabalBot Sopel plugin by Operator873"}
    creds = get_creds()
    # key1, key2, key3, key4 = creds.split("|")
    AUTH = OAuth1(creds.split("|"))

    if action == "post":
        r = requests.post(api, headers=headers, data=payload, auth=AUTH)
    elif action == "authget":
        r = requests.get(api, headers=headers, params=payload, auth=AUTH)
    else:
        r = requests.get(api, headers=headers, params=payload)

    return r.json()


def check_hush(channel):
    db = sqlite3.connect(getdb())
    c = db.cursor()

    hushCheck = c.execute(
        """SELECT * FROM hushchannels WHERE channel=?;""", (channel,)
    ).fetchall()

    db.close()

    if len(hushCheck) > 0:
        return True
    else:
        return False


def feedadmin(bot, trigger):
    # !feedadmin {add/del/list} <target>
    checkquery = """SELECT nick FROM feed_admins WHERE nick=? AND channel=?;"""
    insertnew = """INSERT INTO feed_admins VALUES(?, ?);"""
    deladmin = """DELETE FROM feed_admins WHERE nick=? AND channel=?;"""
    badcommand = "Invalid command. !feedadmin {add/del/list} <targetAccount>"
    admins = ""

    db = sqlite3.connect(getdb())
    c = db.cursor()

    action = trigger.group(3)

    try:
        target = trigger.group(4)
    except ValueError:
        target = None

    if action.lower() == "add":
        check = c.execute(checkquery, (target, trigger.sender)).fetchall()

        if len(check) == 0:
            c.execute(insertnew, (target, trigger.sender))
            db.commit()

            checkagain = c.execute(checkquery, (target, trigger.sender)).fetchall()

            if len(checkagain) > 0:
                bot.say(target + " added as a feed admin in " + trigger.sender)
            else:
                bot.say(
                    "Error inserting new feed admin. Notifying "
                    + bot.settings.core.owner
                )
        else:
            db.close()
            bot.say(target + " is already a feed_admin in this channel.")
            return

    elif action.lower() == "del":
        check = c.execute(checkquery, (target, trigger.sender)).fetchall()

        if len(check) >= 1:
            c.execute(deladmin, (target, trigger.sender))
            db.commit()

            checkagain = c.execute(checkquery, (target, trigger.sender)).fetchall()

            if len(checkagain) == 0:
                bot.say(target + " removed from feed admins in " + trigger.sender)
            else:
                bot.say(
                    "Error removing feed admin. Notifying " + bot.settings.core.owner
                )
        else:
            bot.say(target + " doesn't appear to be a feed admin in this channel.")

    elif action.lower() == "list":
        check = c.execute(
            """SELECT nick FROM feed_admins WHERE channel=?;""", (trigger.sender,)
        ).fetchall()

        for nick in check:
            admins = admins + nick[0] + " "

        bot.say("The following accounts have feed admin in this channel: " + admins)

    else:
        bot.say(badcommand)

    db.close()


def check_feedadmin(target, channel):
    check_query = f"""SELECT nick FROM feed_admins WHERE nick="{target}" AND channel="{channel}";"""
    return len(do_sqlite(check_query, 'all')) > 0


def watcherSpeak(bot, trigger):
    db = sqlite3.connect(getdb())
    c = db.cursor()

    does_exist = c.execute(
        """SELECT * FROM hushchannels WHERE channel=?;""", (trigger.sender,)
    ).fetchall()

    is_feedadmin = c.execute(
        """SELECT * FROM feed_admins WHERE nick=? AND channel=?;""",
        (trigger.account, trigger.sender)
    ).fetchall()

    is_gs = c.execute(
        """SELECT account from globalsysops where nick=?;""", (trigger.nick,)
    ).fetchall()

    if len(does_exist) > 0:
        if (
            len(is_feedadmin) > 0
            or (
                len(is_gs) > 0
                and (
                    trigger.sender == "#wikimedia-gs-internal"
                    or trigger.sender == "#wikimedia-gs"
                )
            )
        ):
            c.execute(
                """DELETE FROM hushchannels WHERE channel=?;""", (trigger.sender,)
            )
            db.commit()
            db.close()
            bot.say("Alright! Back to business.")

        else:
            bot.say("You're not authorized to execute this command.")

    else:
        db.close()
        bot.say(trigger.nick + ": I'm already in 'speak' mode.")


def watcherHush(bot, trigger):
    import time

    db = sqlite3.connect(getdb())
    c = db.cursor()
    now = time.time()
    timestamp = time.ctime(now)

    doesExist = c.execute(
        """SELECT * FROM hushchannels WHERE channel=?;""", (trigger.sender,)
    ).fetchall()

    if len(doesExist) > 0:
        chan, nick, time = doesExist[0]
        bot.say(
            trigger.nick + ": I'm already hushed by " + nick + " since " + time + "."
        )
        db.close()
    else:
        if (
            trigger.sender == "#wikimedia-gs-internal"
            or trigger.sender == "#wikimedia-gs"
        ):
            isGS = c.execute(
                """SELECT account from globalsysops where nick=?;""", (trigger.account,)
            ).fetchall()
            if len(isGS) > 0:
                try:
                    c.execute(
                        """INSERT INTO hushchannels VALUES("%s", "%s", "%s");"""
                        % (trigger.sender, trigger.account, timestamp)
                    )
                    db.commit()
                    check = c.execute(
                        """SELECT * FROM hushchannels WHERE channel=?;""",
                        (trigger.sender,),
                    ).fetchall()[0]
                    chan, nick, time = check
                    bot.say(nick + " hushed! " + time)
                    db.close()
                except:
                    bot.say(
                        "Ugh... something blew up. Help me " + bot.settings.core.owner
                    )

        elif (
            len(
                c.execute(
                    """SELECT nick FROM feed_admins WHERE nick=? AND channel=?;""",
                    (trigger.account, trigger.sender),
                ).fetchall()
            )
            > 0
        ):
            try:
                c.execute(
                    """INSERT INTO hushchannels VALUES(?, ?, ?);""",
                    (trigger.sender, trigger.account, timestamp),
                )
                db.commit()
                check = c.execute(
                    """SELECT * FROM hushchannels WHERE channel=?;""", (trigger.sender,)
                ).fetchall()[0]
                chan, nick, time = check
                bot.say(nick + " hushed! " + time)
                db.close()
            except:
                bot.say("Ugh... something blew up. Help me " + bot.settings.core.owner)

        else:
            bot.say("You're not authorized to execute this command.")


def namespaces(trigger):
    response = ""
    listSpaces = {
        "0": "Article",
        "1": "Article talk",
        "2": "User",
        "3": "User talk",
        "4": "Wikipedia",
        "5": "Wikipedia talk",
        "6": "File",
        "7": "File talk",
        "8": "MediaWiki",
        "9": "MediaWiki talk",
        "10": "Template",
        "11": "Template talk",
        "12": "Help",
        "13": "Help talk",
        "14": "Category",
        "15": "Category talk",
        "101": "Portal",
        "102": "Portal talk",
        "118": "Draft",
        "119": "Draft talk",
        "710": "TimedText",
        "711": "TimedText talk",
        "828": "Module",
        "829": "Module talk",
        "2300": "Gadget",
        "2301": "Gadget talk",
    }
    search = trigger.group(2)

    if search == "" or search is None:
        num, space = random.choice(list(listSpaces.items()))
        response = num + " is " + space + ". Try '!namespace User' or '!namespace 10'"
    else:
        for item in listSpaces:
            if listSpaces[item].lower() == search.lower():
                response = item
            elif item == search:
                response = listSpaces[item]

        if response == "":
            response = "I can't find that name space. Global watch should still work, I just can't provide an example."

    return response


def ignored_nick(nick):
    db = sqlite3.connect(getdb())
    c = db.cursor()

    is_ignored = c.execute(
        """SELECT * FROM ignore_nicks WHERE target=?;""", (nick,)
    ).fetchall()
    db.close()

    if len(is_ignored) > 0:
        return True
    else:
        return False


def get_csrf(project):
    req_token = {"action": "query", "format": "json", "meta": "tokens"}

    d = xmit(project, req_token, "authget")

    try:
        csrf = d["query"]["tokens"]["csrftoken"]
        return csrf
    except KeyError:
        return False
