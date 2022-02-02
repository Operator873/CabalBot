import sqlite3
import cabalutil

def report(bot, change):

    gs = change["user"]
    gs_list = None

    db = sqlite3.connect(bot.memory["cabaldb"])
    c = db.cursor()

    try:
        gs_list = c.execute(
            """SELECT account FROM globalsysops WHERE account=?;""", (gs,)
        ).fetchall()
    except:
        pass
    finally:
        db.close()

    report = None

    no_action = [
        "NEWUSERS",
        "RIGHTS",
        "PATROL",
        "REVIEW",
        "ABUSEFILTER",
        "MASSMESSAGE",
        "RENAMEUSER",
        "MOVE",
        "IMPORT",
        "PAGETRANSLATION",
        "THANKS",
    ]

    if len(gs_list) > 0 and gs_list is not None:

        action = str(change["log_type"]).upper()
        pageLink = change["meta"]["uri"]
        editor = change["user"][:2] + "\u200B" + change["user"][2:]
        comment = str(change["comment"]).replace("\n", "")

        if action in no_action:
            return
        elif action == "BLOCK":
            flags = change["log_params"]["flags"]
            duration = change["log_params"]["duration"]
            actionType = change["log_action"]
            report = (
                "Log action: "
                + action
                + " || "
                + editor
                + " "
                + actionType
                + "ed "
                + pageLink
                + " Flags: "
                + flags
                + " Duration: "
                + duration
                + " Comment: "
                + comment[:200]
            )
        elif action == "ABUSEFILTER":
            report = action + " activated by " + editor + " " + pageLink
        elif action == "MOVE":
            report = (
                "Log action: "
                + action
                + " || "
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
                + " || "
                + editor
                + " "
                + pageLink
                + " "
                + comment[:200]
            )

        if report is not None:
            channel = "#wikimedia-gs-internal"

            if cabalutil.check_hush(channel) is True:
                return
            else:
                bot.say(report, channel)
    else:
        return


def check(project):
    db = sqlite3.connect(bot.memory["cabaldb"])
    c = db.cursor()

    check = c.execute(
        """SELECT * FROM GSwikis WHERE project=?;""", (project,)
    ).fetchall()

    db.close()

    if len(check) > 0:
        return True
    else:
        return False