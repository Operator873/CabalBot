import sys
sys.path.insert(0, "/path/to/.sopel/plugins/cabalbot") # Help Sopel find the submodules we are about to load

import affeed
import autolink
import cabalutil
import confirmedfeed
import globalwatch
import gstools
import oresfeed
import pagewatch
import pushover
import rcfeed

import json
import threading
from sopel import plugin
from sseclient import SSEClient as EventSource

# Set some globals because repeating yourself is annoying
BOTADMINMSG = "This command is only available to the bot admins."
CHANCMDMSG = "This message must be used in a channel."


def setup(bot):
    # Configure the RC feed listener, save to bot memory, and start it.
    stop_event = threading.Event()
    url = "https://stream.wikimedia.org/v2/stream/recentchange"
    listen = threading.Thread(target=listener, args=(bot, url, stop_event))
    bot.memory["wikistream_stop"] = stop_event
    bot.memory["wikistream_listener"] = listen
    bot.memory["wikistream_listener"].start()

    # Configure the ORES feed listener, save to bot memory, and start it.
    ores_url = "https://stream.wikimedia.org/v2/stream/revision-score"
    ores = threading.Thread(target=ores_listener, args=(bot, ores_url, stop_event))
    bot.memory["ores_stop"] = stop_event
    bot.memory["ores"] = ores
    bot.memory["ores"].start()


def listener(bot, url, stop_event):
    # Listen to EventStream for Recent Changes
    while not stop_event.is_set():
        for event in EventSource(url):
            # Check for stop flag inside the loop
            if stop_event.is_set():
                return

            if event.event == "message":
                # Sometimes the EventStream sends garbage, discard if necessary
                try:
                    change = json.loads(event.data)
                    dispatch(bot, change)
                except ValueError:
                    pass


def ores_listener(bot, url, stop_event):
    # Listen to EventStream for ORES events
    while not stop_event.is_set():
        for event in EventSource(url):
            # Check for stop flag inside the loop
            if stop_event.is_set():
                return

            if event.event == "message":
                # Sometimes the EventStream sends garbage, discard if necessary
                try:
                    change = json.loads(event.data)
                    ores_dispatch(bot, change)
                except ValueError:
                    pass


def dispatch(bot, change):
    # Dispatch edits and page creations
    if change["type"] == "edit" or change["type"] == "new":
        # Check for specific pages in watch
        if pagewatch.check(change):
            pagewatch.report(bot, change)

        # Check for pages watched globally
        if globalwatch.check(change):
            globalwatch.report(bot, change)

        # If bot is Bot873, check for cssjs reporting
        if (
            pagewatch.checkcss(change)
            and bot.nick == "Bot873"
        ):
            pagewatch.cssjs(bot, change)

    # If rc feed is being reported for a project, dispatch report
    if rcfeed.check(change):
        rcfeed.report(bot, change)

    # If edits from un-confirmed accounts are being reported, dispatch report
    if confirmedfeed.check(change):
        confirmedfeed.report(bot, change)

    # Dispatch Log events
    if change["type"] == "log":
        # Handles GS Log events
        if gstools.check(change["wiki"]):
            gstools.report(bot, change)

        # If abuse filter hits are being reported, dispatch report
        if change["log_type"] == "abusefilter":
            if affeed.check(change):
                affeed.report(bot, change)


def ores_dispatch(bot, change):
    # Dispatch ORES reports
    if oresfeed.check(change):
        oresfeed.report(bot, change)


@plugin.require_admin(message=BOTADMINMSG)
@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("feedadmin")
def feedcmd(bot, trigger): # !feedadmin {add/del/list} <target>
    cabalutil.feedadmin(bot, trigger)


@plugin.command("speak")
def set_speak(bot, trigger): # Removes the channel from hushchannels and allows the bot to speak
    cabalutil.watcherSpeak(bot, trigger)


@plugin.command("hush")
@plugin.command("mute")
def do_hush(bot, trigger): # Adds the channel to hushchannels where the bot will not speak
    cabalutil.watcherHush(bot, trigger)


@plugin.require_admin(message=BOTADMINMSG)
@plugin.command("watchstart")
def start_listener(bot, trigger): # Manually restart listeners
    if "wikistream_listener" not in bot.memory:
        stop_event = threading.Event()
        bot.memory["wikistream_stop"] = stop_event
        url = "https://stream.wikimedia.org/v2/stream/recentchange"
        listen = threading.Thread(
            target=listener, args=(bot, url, bot.memory["wikistream_stop"])
        )
        bot.memory["wikistream_listener"] = listen

    if "ores" not in bot.memory:
        stop_event = threading.Event()
        bot.memory["ores_stop"] = stop_event
        ores_url = "https://stream.wikimedia.org/v2/stream/revision-score"
        listen = threading.Thread(
            target=ores_listener, args=(bot, ores_url, bot.memory["ores_stop"])
        )
        bot.memory["ores"] = listen

    bot.memory["wikistream_listener"].start()
    bot.memory["ores"].start()
    bot.say("Listening to EventStreams...")


@plugin.interval(120)
def checkListener(bot): # Verify listeners are still listening every 2 mins and restart if needed
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

    if bot.memory["ores"].is_alive() is not True:
        del bot.memory["ores"]
        del bot.memory["ores_stop"]

        stop_event = threading.Event()
        bot.memory["ores_stop"] = stop_event
        ores_url = "https://stream.wikimedia.org/v2/stream/revision-score"
        listen = threading.Thread(
            target=ores_listener, args=(bot, ores_url, bot.memory["ores_stop"])
        )
        bot.memory["ores"] = listen

        bot.memory["ores"] = listen
        bot.memory["ores"].start()


@plugin.require_admin(message=BOTADMINMSG)
@plugin.command("watchstatus")
def watchStatus(bot, trigger): # Have the bot report the status of the listeners
    if (
        "wikistream_listener" in bot.memory
        and bot.memory["wikistream_listener"].is_alive() is True
    ):
        bot.say("RC stream listener is alive.")
    else:
        bot.say("RC stream listener is dead.")

    if (
        "ores" in bot.memory
        and bot.memory["ores"].is_alive() is True
    ):
        bot.say("ORES listener is alive.")
    else:
        bot.say("ORES listener is dead.")


@plugin.require_admin(message=BOTADMINMSG)
@plugin.command("watchstop")
def watchStop(bot, trigger): # Force the listeners to halt and deletes the thread from memory
    if "wikistream_listener" not in bot.memory:
        bot.say("RC stream listener isn't running.")
    else:
        try:
            bot.memory["wikistream_stop"].set()
            del bot.memory["wikistream_listener"]
            bot.say("RC stream listener stopped.")
        except Exception as e:
            bot.say(str(e))

    if "ores" not in bot.memory:
        bot.say("ORES listener isn't running.")
    else:
        try:
            bot.memory["ores_stop"].set()
            del bot.memory["ores"]
            bot.say("ORES listener stopped.")
        except Exception as e:
            bot.say(str(e))


@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("watch")
def watch(bot, trigger): # add a new specific page to watch on a specific project
    watchAction = trigger.group(3)
    if watchAction == "add" or watchAction == "Add" or watchAction == "+":
        if trigger.group(5) == "":
            bot.say("Command seems malformed. Syntax: !watch add proj page")
        else:
            bot.say(
                pagewatch.watcherAdd(trigger.group(2), trigger.account, trigger.sender)
            )
    elif watchAction == "del" or watchAction == "Del" or watchAction == "-":
        if trigger.group(5) == "":
            bot.say("Command seems malformed. Syntax: !watch del proj page")
        else:
            bot.say(
                pagewatch.watcherDel(trigger.group(2), trigger.account, trigger.sender)
            )
    elif watchAction == "ping" or watchAction == "Ping":
        if trigger.group(6) == "":
            bot.say("Command seems malformed. Syntax: !watch ping <on/off> proj page")
        else:
            bot.say(
                pagewatch.watcherPing(trigger.group(2), trigger.account, trigger.sender)
            )
    else:
        bot.say("I don't recognzie that command. Options are: Add & Del")


# !globalwatch ping on namespaceid title
# !globalwatch add namespaceid title
@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("globalwatch")
def gwatch(bot, trigger): # Globally watch a page in a certain namespace
    watchAction = trigger.group(3)
    if watchAction == "add" or watchAction == "Add" or watchAction == "+":
        if trigger.group(5) == "" or trigger.group(5) is None:
            bot.say(
                "Command seems malformed. Syntax: !globalwatch add namespaceID page"
            )
        else:
            bot.say(
                globalwatch.addpage(trigger.group(2), trigger.account, trigger.sender)
            )
    elif watchAction == "del" or watchAction == "Del" or watchAction == "-":
        if trigger.group(5) == "" or trigger.group(5) is None:
            bot.say(
                "Command seems malformed. Syntax: !globalwatch del namespaceID page"
            )
        else:
            bot.say(
                globalwatch.delpage(trigger.group(2), trigger.account, trigger.sender)
            )
    elif watchAction == "ping" or watchAction == "Ping":
        if trigger.group(6) == "" or trigger.group(6) is None:
            bot.say(
                "Command seems malformed. Syntax: !globalwatch ping <on/off> namespaceID page"
            )
        else:
            bot.say(globalwatch.ping(trigger.group(2), trigger.account, trigger.sender))
    else:
        bot.say("I don't recognize that command. Options are: add, del, & ping")


@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("namespace")
def get_namespace(bot, trigger): # Get namespace information by either number or name
    bot.say(cabalutil.namespaces(trigger))


@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("abusefeed", "affeed")
def do_affeed(bot, trigger): # !abusefeed {start/stop} <project> || Controls the Abuse Filter feed for this channel
    try:
        action, project = trigger.group(2).split(' ', 1)
    except ValueError:
        bot.say("Missing project! Syntax: !abusefeed {start/stop} <project>")
        return

    if action.lower() == "start":
        bot.say(affeed.start(trigger))
    elif action.lower() == "stop":
        bot.say(affeed.stop(trigger))
    else:
        bot.say("I'm not sure how to " + action + ". Try 'start' and 'stop'.")


@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("rcfeed")
def do_rcfeed(bot, trigger): # !rcfeed {start/stop} <project> || Controls the rc feed for this channel
    try:
        action, project = trigger.group(2).split(' ', 1)
    except ValueError:
        bot.say("Missing project! Syntax: !rcfeed {start/stop} <project>")
        return

    if action.lower() == "start":
        bot.say(rcfeed.start(trigger))
    elif action.lower() == "stop":
        bot.say(rcfeed.stop(trigger))
    else:
        bot.say("I'm not sure how to " + action + ". Try 'start' and 'stop'.")

@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("confirmedfeed")
def do_confirmedfeed(bot, trigger):
    # !confirmedfeed {start/stop} <project> || Controls the Confirmed feed for this channel
    try:
        action, project = trigger.group(2).split(' ', 1)
    except ValueError:
        bot.say("Missing project! Syntax: !confirmedfeed {start/stop} <project>")
        return

    if action.lower() == "start":
        bot.say(confirmedfeed.start(trigger))
    elif action.lower() == "stop":
        bot.say(confirmedfeed.stop(trigger))
    else:
        bot.say("I'm not sure how to " + action + ". Try 'start' and 'stop'.")


@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("oresfeed", "vandalfeed", "vandalismfeed")
def do_oresfeed(bot, trigger): # # !oresfeed {start/stop} <project> || Controls the ORES feed for this channel
    try:
        action, project = trigger.group(2).split(' ', 1)
    except ValueError:
        bot.say("Missing project! Syntax: !oresfeed {start/stop} <project>")
        return

    if action.lower() == "start":
        bot.say(oresfeed.start(trigger))
    elif action.lower() == "stop":
        bot.say(oresfeed.stop(trigger))
    else:
        bot.say("I'm not sure how to " + action + ". Try 'start' and 'stop'.")


@plugin.find(r"\[\[(.*?)\]\]")
def autolinker(bot, trigger): # Autolinker for standard [[wikilinks]]
    if not autolink.checklang(trigger.sender) or cabalutil.ignored_nick(
        trigger.account
    ):
        return

    else:
        url = autolink.getlang(trigger.sender)
        link = trigger.groups()[0].replace(" ", "_")
        if url is None:
            bot.say("I found the channel in the database, but there was no URL saved.")
        else:
            bot.say(url + link)


@plugin.find(r"\{\{(.*?)\}\}")
def autolinker_templates(bot, trigger): # Autolinker for {{Template:}} links
    if not autolink.checklang(trigger.sender) or cabalutil.ignored_nick(
        trigger.account
    ):
        return

    else:
        url = autolink.getlang(trigger.sender)
        link = trigger.groups()[0].replace(" ", "_")
        if url is None:
            bot.say("I found the channel in the database, but there was no URL saved.")
        else:
            bot.say(url + "Template:" + link)


@plugin.require_admin(message=BOTADMINMSG)
@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("setlang")
def setlang(bot, trigger): # Set the preferred language for a channel for Autolinks
    # !setlang enwiki https://enwp.org/
    if not trigger.group(4):
        bot.say("Missing URL! Syntax is !setlang <project> <baseURL>")
        return

    if autolink.addlang(trigger.sender, trigger.group(3), trigger.group(4)):
        bot.say(trigger.sender + " will use " + trigger.group(4))


@plugin.require_admin(message=BOTADMINMSG)
@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("unsetlang")
def unsetlang(bot, trigger): # Clear the set language for auto links (disables autolink)
    if autolink.rmvlang(trigger.sender):
        bot.say(trigger.sender + " was cleared.")


@plugin.require_admin(message=BOTADMINMSG)
@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("ignorenick")
def setignorenick(bot, trigger): # Tell the bot to NOT do autolinks for the provided IRC account name
    # !ignorenick <ircAccountName>
    if autolink.ignorenick(trigger.group(3), trigger.account):
        bot.say("I'll ignore links from " + trigger.group(3) + " from now on.")


@plugin.require_admin(message=BOTADMINMSG)
@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("unignorenick")
def setunignorenick(bot, trigger): # Tell the bot to allow the IRC account to be autolinked again
    # !unignorenick <ircAccountName>
    if autolink.unignorenick(trigger.group(3)):
        bot.say("I'll stop ignoring links from " + trigger.group(3) + ".")


@plugin.require_owner(message="This command is only available to the bot owner.")
@plugin.command("restartbot", "restart")
def do_bot_restart(bot, trigger): # Order the bot to restart with any provided message
    if trigger.group(2):
        bot.restart("Restarting by order of " + trigger.account + " Reason: " + trigger.group(2))
    else:
        bot.restart("Restarting by order of " + trigger.account)


@plugin.require_owner(message="This command is only available to the bot owner.")
@plugin.command("botdie", "quit")
def do_botdie(bot, trigger): # Order the bot to quit with the provided message
    if trigger.group(2):
        bot.quit("Bot ordered to die by " + trigger.account + " Reason: " + trigger.group(2))
    else:
        bot.quit("Bot ordered to die by " + trigger.account)


@plugin.command("commands", "help", "doc")
def get_help(bot, trigger):
    bot.say(trigger.nick + ": My documentation can be found at https://github.com/Operator873/CabalBot")

##########################################
#      GlobalSysBot Commands follow      #
##########################################

@plugin.command("onirc")
def do_onirc(bot, trigger): # Let GlobalSysBot
    data = gstools.on_irc(trigger.group(3))

    if data["ok"]:
        for item in data["data"]:
            bot.say(item)
        if data["more"]:
            bot.say(
                "There are more pages listed. Re-run !onirc "
                + trigger.group(3)
                + " after deleting the above pages."
            )
    else:
        bot.say(data["msg"])


@plugin.require_admin(message=BOTADMINMSG)
@plugin.command("addmember")
def do_addmember(bot, trigger):
    bot.say(gstools.addGS(trigger))


@plugin.require_admin(message=BOTADMINMSG)
@plugin.command("removemember")
def do_delmember(bot, trigger):
    bot.say(gstools.delGS(trigger))

@plugin.require_admin(message=BOTADMINMSG)
@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("addwiki")
def add_wiki(bot, trigger):
    if trigger.group(5) == "":
        bot.say("Seems to be missing something. Syntax is !addwiki <project> <apiurl> <categoryname>")
    else:
        bot.say(gstools.add_wiki(trigger.group(3), trigger.group(4), trigger.group(5)))


@plugin.require_admin(message=BOTADMINMSG)
@plugin.require_chanmsg(CHANCMDMSG)
@plugin.command("delwiki")
def add_wiki(bot, trigger):
    bot.say(gstools.del_wiki(trigger.group(3)))


@plugin.require_admin()
@plugin.require_chanmsg("This command must be used in a channel.")
@plugin.command("admin@simplewiki", "admin")
def regular_ping(bot, trigger):
    if (
        trigger.sender == "#wikipedia-simple"
        or trigger.sender == "#wikipedia-simple-admins"
    ):
        msg = (
            trigger.nick
            + " in "
            + trigger.sender
            + " pinged admins with message: "
            + trigger.group(2)
        )
        if pushover.send_alert(msg, 0):
            bot.say("Sending pushover alerts to opted-in admins as well.")
        else:
            bot.say("Something broke when I was attempting pushover notifications.")


@plugin.require_chanmsg("This command must be used in a channel.")
@plugin.command("testpushover")
def test_ping(bot, trigger):
    if (
        trigger.sender == "#wikipedia-simple"
        or trigger.sender == "#wikipedia-simple-admins"
    ):
        msg = (
            trigger.nick
            + " in "
            + trigger.sender
            + " trigger a test notification with message: "
            + trigger.group(2)
        )

        if pushover.send_alert(msg, -2):
            bot.say("Sending pushover test alert.")
        else:
            bot.say("Something broke when I was attempting pushover notifications.")
