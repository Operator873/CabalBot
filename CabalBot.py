import sys
sys.path.insert(0, '/path/to/sopel/plugins/cabalbot')

import affeed
import rcfeed
import gstools
import cabalutil
import globalwatch
import pagewatch
import json
import threading
import sqlite3
import random
from sopel import plugin
from sseclient import SSEClient as EventSource


BOTADMINMSG = "This command is only available to the bot admins."
CHANCMDMSG = "This message must be used in a channel."


def setup(bot):
    stop_event = threading.Event()
    url = "https://stream.wikimedia.org/v2/stream/recentchange"
    listen = threading.Thread(target=listener, args=(bot, url, stop_event))
    bot.memory["wikistream_stop"] = stop_event
    bot.memory["wikistream_listener"] = listen


def listener(bot, url, stop_event):
    while not stop_event.is_set():
        for event in EventSource(url):
            if stop_event.is_set():
                return
            else:
                if event.event == "message":
                    try:
                        change = json.loads(event.data)
                        dispatch(bot, change)
                    except ValueError:
                        pass


def dispatch(bot, change):

    if change["type"] == "edit" or change["type"] == "new":
        if pagewatch.check(change):
            pagewatch.report(bot, change)

        if globalwatch.check(change):
            globalwatch.report(bot, change)

        if pagewatch.checkcss(change):
            pagewatch.cssjs(bot, change)

    if rcfeed.check(change):
        rcfeed.report(bot, change)

    if change["type"] == "log":
        if gstools.check(change["wiki"]):
            gstools.report(bot, change)
        if affeed.check(change):
            affeed.report(bot, change)


@plugin.require_admin(message=BOTADMINMSG)
@plugin.require_chanmsg(message=CHANCMDMSG)
@plugin.command("feedadmin")
def feedadmin(bot, trigger):
    # !feedadmin {add/del/list} <target>
    checkquery = """SELECT nick FROM feed_admins WHERE nick=? AND channel=?;"""
    insertnew = """INSERT INTO feed_admins VALUES(?, ?);"""
    deladmin = """DELETE FROM feed_admins WHERE nick=? AND channel=?;"""
    badcommand = "Invalid command. !feedadmin {add/del/list} <targetAccount>"
    admins = ""

    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    action = trigger.group(3)
    if trigger.group(4) is not None:
        target = trigger.group(4)

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


@plugin.command("speak")
def watcherSpeak(bot, trigger):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    doesExist = c.execute(
        """SELECT * FROM hushchannels WHERE channel=?;""", (trigger.sender,)
    ).fetchall()

    if len(doesExist) > 0:
        try:
            if (
                len(
                    c.execute(
                        """SELECT nick FROM feed_admins WHERE nick=? AND channel=?;""",
                        (trigger.account, trigger.sender),
                    ).fetchall()
                )
                > 0
            ):
                c.execute(
                    """DELETE FROM hushchannels WHERE channel=?;""", (trigger.sender,)
                )
                db.commit()
                bot.say("Alright! Back to business.")
            else:
                bot.say("You're not authorized to execute this command.")
        except:
            bot.say("Ugh... something blew up. Help me " + bot.settings.core.owner)
        finally:
            db.close()
    else:
        db.close()
        bot.say(trigger.nick + ": I'm already in 'speak' mode.")


@plugin.command("hush")
@plugin.command("mute")
def watcherHush(bot, trigger):
    import time

    db = sqlite3.connect(cabalutil.getdb())
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
                """SELECT account from globalsysops where nick=?;""", (trigger.nick,)
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


@plugin.require_admin(message=BOTADMINMSG)
@plugin.command("watchstart")
def start_listener(bot, trigger):
    if "wikistream_listener" not in bot.memory:
        stop_event = threading.Event()
        bot.memory["wikistream_stop"] = stop_event
        url = "https://stream.wikimedia.org/v2/stream/recentchange"
        listen = threading.Thread(
            target=listener, args=(bot, url, bot.memory["wikistream_stop"])
        )
        bot.memory["wikistream_listener"] = listen
    bot.memory["wikistream_listener"].start()
    bot.say("Listening to EventStream...")


@plugin.interval(120)
def checkListener(bot):
    if bot.memory["wikistream_listener"].is_alive() is not True:
        del bot.memory["wikistream_listener"]
        del bot.memory["wikistream_stop"]

        stop_event = threading.Event()
        bot.memory["wikistream_stop"] = stop_event
        url = "https://stream.wikimedia.org/v2/stream/recentchange"

        listen = threading.Thread(
            target=listener, args=(bot, url, bot.memory["wikistream_stop"])
        )

        bot.memory["wikistream_listener"] = listen
        bot.memory["wikistream_listener"].start()
    else:
        pass


@plugin.require_admin(message=BOTADMINMSG)
@plugin.command("watchstatus")
def watchStatus(bot, trigger):
    if (
        "wikistream_listener" in bot.memory
        and bot.memory["wikistream_listener"].is_alive() is True
    ):
        msg = "Listener is alive."
    else:
        msg = "Listener is dead."

    bot.say(msg)


@plugin.require_admin(message=BOTADMINMSG)
@plugin.command("watchstop")
def watchStop(bot, trigger):
    if "wikistream_listener" not in bot.memory:
        bot.say("Listener isn't running.")
    else:
        try:
            bot.memory["wikistream_stop"].set()
            del bot.memory["wikistream_listener"]
            bot.say("Listener stopped.")
        except Exception as e:
            bot.say(str(e))


@plugin.require_admin(message=BOTADMINMSG)
@plugin.command("addmember")
def addGS(bot, trigger):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()
    c.execute(
        """INSERT INTO globalsysops VALUES(?, ?);""",
        (trigger.group(3), trigger.group(4)),
    )
    db.commit()
    nickCheck = c.execute(
        """SELECT nick FROM globalsysops where account=?;""", (trigger.group(4),)
    ).fetchall()
    nicks = ""
    for nick in nickCheck:
        if nicks == "":
            nicks = nick[0]
        else:
            nicks = nicks + " " + nick[0]
    db.close()
    bot.say(
        "Wikipedia account "
        + trigger.group(4)
        + " is now known by IRC nick(s): "
        + nicks
    )


@plugin.require_admin(message=BOTADMINMSG)
@plugin.command("removemember")
def delGS(bot, trigger):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()
    c.execute("""DELETE FROM globalsysops WHERE account=?;""", (trigger.group(3),))
    db.commit()
    checkWork = None
    try:
        checkWork = c.execute(
            """SELECT nick FROM globalsysops WHERE account=?;""", (trigger.group(3),)
        ).fetchall()
        bot.say("All nicks for " + trigger.group(3) + " have been purged.")
    except:
        bot.say("Ugh... Something blew up. Help me " + bot.settings.core.owner)


@plugin.require_chanmsg(message=CHANCMDMSG)
@plugin.command("watch")
def watch(bot, trigger):
    watchAction = trigger.group(3)
    if watchAction == "add" or watchAction == "Add" or watchAction == "+":
        if trigger.group(5) == "":
            bot.say("Command seems malformed. Syntax: !watch add proj page")
        else:
            bot.say(watcherAdd(trigger.group(2), trigger.account, trigger.sender))
    elif watchAction == "del" or watchAction == "Del" or watchAction == "-":
        if trigger.group(5) == "":
            bot.say("Command seems malformed. Syntax: !watch del proj page")
        else:
            bot.say(watcherDel(trigger.group(2), trigger.account, trigger.sender))
    elif watchAction == "ping" or watchAction == "Ping":
        if trigger.group(6) == "":
            bot.say("Command seems malformed. Syntax: !watch ping <on/off> proj page")
        else:
            bot.say(watcherPing(trigger.group(2), trigger.account, trigger.sender))
    else:
        bot.say("I don't recognzie that command. Options are: Add & Del")


# !globalwatch ping on namespaceid title
# !globalwatch add namespaceid title
@plugin.require_chanmsg(message=CHANCMDMSG)
@plugin.command("globalwatch")
def gwatch(bot, trigger):
    watchAction = trigger.group(3)
    if watchAction == "add" or watchAction == "Add" or watchAction == "+":
        if trigger.group(5) == "" or trigger.group(5) is None:
            bot.say(
                "Command seems malformed. Syntax: !globalwatch add namespaceID page"
            )
        else:
            bot.say(globalWatcherAdd(trigger.group(2), trigger.account, trigger.sender))
    elif watchAction == "del" or watchAction == "Del" or watchAction == "-":
        if trigger.group(5) == "" or trigger.group(5) is None:
            bot.say(
                "Command seems malformed. Syntax: !globalwatch del namespaceID page"
            )
        else:
            bot.say(globalWatcherDel(trigger.group(2), trigger.account, trigger.sender))
    elif watchAction == "ping" or watchAction == "Ping":
        if trigger.group(6) == "" or trigger.group(6) is None:
            bot.say(
                "Command seems malformed. Syntax: !globalwatch ping <on/off> namespaceID page"
            )
        else:
            bot.say(
                globalWatcherPing(trigger.group(2), trigger.account, trigger.sender)
            )
    else:
        bot.say("I don't recognize that command. Options are: add, del, & ping")


@plugin.require_chanmsg(message=CHANCMDMSG)
@plugin.command("namespace")
def namespaces(bot, trigger):
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
    response = ""

    if search == "" or search is None:
        bot.say("Randomly showing an example. Try '!namespace User' or '!namespace 10'")
        num, space = random.choice(list(listSpaces.items()))
        bot.say(num + " is " + space)
    else:
        for item in listSpaces:
            if listSpaces[item].lower() == search.lower():
                response = item
            elif item == search:
                response = listSpaces[item]

        if response == "":
            bot.say(
                "I can't find that name space. Global watch should still work, I just can't provide an example."
            )
        else:
            bot.say(response)
