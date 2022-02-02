import cabalutil
import sqlite3


def check(change):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    RC_exists = c.execute(
        """SELECT * FROM rc_feed WHERE project=?;""", (change["wiki"],)
    ).fetchall()

    db.close()

    if len(RC_exists) > 0:
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
        space = u"\u200B"
        editor = change["user"][:2] + space + change["user"][2:]
        logLink = (
            change["server_url"]
            + "/wiki/Special:AbuseLog/"
            + str(change["log_params"]["log"])
        )
        filterNumber = change["log_params"]["filter"]

        report = (
            "Abuse Filter "
            + filterNumber
            + " was activated by "
            + editor
            + " at "
            + pageLink
            + " "
            + logLink
        )

        if report is not None:
            for chan in channel:
                if cabalutil.check_hush(chan) is True:
                    return
                else:
                    bot.say(report, chan)


