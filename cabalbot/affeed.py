import cabalutil
import sqlite3
from sopel import formatting


def check(change):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    AF_exists = c.execute(
        """SELECT * FROM af_feed WHERE project=?;""", (change["wiki"],)
    ).fetchall()

    db.close()

    if len(AF_exists) > 0:
        return True
    else:
        return False


def report(bot, change):
    project = change["wiki"]

    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    channel = c.execute(
        """SELECT channel FROM af_feed WHERE project=?;""", (project,)
    ).fetchall()

    if len(channel) > 0:

        pageLink = change["meta"]["uri"]
        editor = change["user"]
        logLink = (
            change["server_url"]
            + "/wiki/Special:AbuseLog/"
            + str(change["log_params"]["log"])
        )
        filterNumber = change["log_params"]["filter"]

        report = (
            formatting.color(formatting.bold(editor), formatting.colors.BLUE)
            + " activated "
            + formatting.color(formatting.bold("Abuse Filter "), formatting.colors.RED)
            + formatting.color(formatting.bold(filterNumber), formatting.colors.RED)
            + " on "
            + pageLink
            + formatting.color(" || Log Entry: ", formatting.colors.GREEN)
            + logLink
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
        """SELECT channel FROM af_feed WHERE project=? and channel=?;""",
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
        c.execute("""INSERT INTO af_feed VALUES(?, ?);""", (project, channel))
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
            """DELETE FROM af_feed WHERE project=? and channel=?;""", (project, channel)
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
            "You are not authorized to start the Abuse Filter feed in this channel."
        )
        return response

    if checkchannel(trigger.group(4), trigger.sender):
        response = "I'm already reporting Abuse Filter hits in this channel."
        return response

    if add_channel(trigger.group(4), trigger.sender):
        response = (
            "I will report Abuse Filter activations on "
            + trigger.group(4)
            + " in this channel."
        )
    else:
        response = "An unknown error occurred during addition to database."

    return response


def stop(trigger):
    if not cabalutil.check_feedadmin(trigger.account, trigger.sender):
        response = (
            "You are not authorized to start the Abuse Filter feed in this channel."
        )
        return response

    if not checkchannel(trigger.group(4), trigger.sender):
        response = "I'm not reporting Abuse Filter hits in this channel."
        return response

    if del_channel(trigger.group(4), trigger.sender):
        response = (
            "Abuse Filter reports for " + trigger.group(4) + " have been stopped."
        )
    else:
        response = "An unknown error occurred during removal from the database."

    return response
