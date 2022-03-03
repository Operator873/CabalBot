import cabalutil
import sqlite3
from sopel import formatting


SAFEGROUPS = [
    "autoconfirmed",
    "bot",
    "sysop",
    "steward"
]


def check(change):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    RC_exists = c.execute(
        """SELECT * FROM ores_feed WHERE project=?;""", (change["database"],)
    ).fetchall()

    db.close()

    if len(RC_exists) > 0:
        return True
    else:
        return False


def report(bot, change):
    proj = change["database"]
    report = None
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    channel = c.execute(
        """SELECT channel FROM ores_feed WHERE project=?;""", (proj,)
    ).fetchall()

    db.close()

    try:
        damaging = change["scores"]["damaging"]["prediction"][0]
        goodfaith = change["scores"]["goodfaith"]["prediction"][0]
    except KeyError:
        return

    if channel is not None:
        if damaging == "true" and goodfaith == "false":
            # Check the editing nick for safe group memberships. If one found, stop further processing
            actor_groups = change["performer"]["user_groups"]
            for i in SAFEGROUPS:
                if i in actor_groups:
                    return

            actor = change["performer"]["user_text"]
            editor = actor[:2] + "\u200B" + actor[2:]
            title = formatting.color(change["page_title"], formatting.colors.GREEN)
            project = change["meta"]["domain"]
            revid = str(change["rev_id"])
            prob = change["scores"]["damaging"]["probability"]["true"]
            link = "https://" + project + "/w/index.php?diff=" + revid
            if "comment" in change:
                comment = change["comment"]
            else:
                comment = "<no edit comment>"

            report = (
                "\x02"
                + title
                + "\x02 may have been vandalized (probability: "
                + "{:.0%}".format(prob)
                + ") by "
                + formatting.color(formatting.bold(editor), formatting.colors.RED)
                + " "
                + link
                + " "
                + comment
            )

        if report is not None:
            for chan in channel:
                if cabalutil.check_hush(chan[0]) is True:
                    return
                else:
                    bot.say(report, chan[0])


def checkchannel(project, channel):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    check = c.execute(
        """SELECT channel FROM ores_feed WHERE project=? and channel=?;""",
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
        c.execute("""INSERT INTO ores_feed VALUES(?, ?);""", (project, channel))
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
            """DELETE FROM ores_feed WHERE project=? and channel=?;""", (project, channel)
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
            "You are not authorized to start the ORES RC feed in this channel."
        )
        return response

    if checkchannel(trigger.group(4), trigger.sender):
        response = (
            "I'm already reporting damaging edits for "
            + trigger.group(4)
            + " in this channel."
        )
        return response

    if add_channel(trigger.group(4), trigger.sender):
        response = (
            "I will report damaging edits on " + trigger.group(4) + " in this channel."
        )
    else:
        response = "An unknown error occurred during addition to database."

    return response


def stop(trigger):
    if not cabalutil.check_feedadmin(trigger.account, trigger.sender):
        response = (
            "You are not authorized to stop the ORES RC feed in this channel."
        )
        return response

    if not checkchannel(trigger.group(4), trigger.sender):
        response = "I'm not reporting damaging edits in this channel."
        return response

    if del_channel(trigger.group(4), trigger.sender):
        response = "Damaging edits for " + trigger.group(4) + " have been stopped."
    else:
        response = "An unknown error occurred during removal from the database."

    return response
