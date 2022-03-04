import cabalutil
import sqlite3
from sopel import formatting


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
    proj = change["wiki"]
    report = None
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    channel = c.execute(
        """SELECT channel FROM rc_feed WHERE project=?;""", (proj,)
    ).fetchall()

    if channel is not None:
        if change["type"] == "log":
            no_action = [
                "ABUSEFILTER",
                "IMPORT",
                "MASSMESSAGE",
                "PAGETRANSLATION",
                "PATROL",
                "RENAMEUSER",
                "REVIEW",
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
            elif action == "BLOCK":
                if subType == "UNBLOCK":
                    report = (
                        formatting.color(formatting.bold("Log action: "), formatting.color.RED)
                        + action
                        + " || "
                        + editor
                        + " unblocked "
                        + pageLink
                        + " Comment: "
                        + comment[:200]
                    )
                else:
                    flags = change["log_params"]["flags"]
                    duration = change["log_params"]["duration"]

                    report = (
                        formatting.color(formatting.bold("Log action: "), formatting.color.RED)
                        + action
                        + " || "
                        + editor
                        + " "
                        + subType
                        + "ed "
                        + pageLink
                        + " Flags: "
                        + flags
                        + " Duration: "
                        + duration
                        + " Comment: "
                        + comment[:200]
                    )
            elif action == "MOVE":
                report = (
                    formatting.color(formatting.bold("Log action: "), formatting.color.RED)
                    + action
                    + " || "
                    + editor
                    + " moved "
                    + pageLink
                    + " "
                    + comment[:200]
                )
            elif action == "NEWUSERS":
                report = (
                    formatting.color(formatting.bold("Log action: "), formatting.color.RED)
                    + action
                    + " || New user "
                    + pageLink
                    + " was created."
                )
            elif action == "RIGHTS":
                newGroups = change["log_params"]["newgroups"]
                oldGroups = change["log_params"]["oldgroups"]
                report = (
                    formatting.color(formatting.bold("Log action: "), formatting.color.RED)
                    + action
                    + " || "
                    + editor
                    + " changed rights for "
                    + pageLink
                    + " added: "
                    + newGroups
                    + " removed: "
                    + oldGroups
                    + " "
                    + comment[:200]
                )
            elif action == "DELETE":
                if subType == "RESTORE":
                    report = (
                        formatting.color(formatting.bold("Log action: "), formatting.color.RED)
                        + action
                        + " || "
                        + editor
                        + " restored "
                        + pageLink
                        + " "
                        + comment[:200]
                    )
                elif subType == "REVISION":
                    revID = change["log_params"]["ids"]
                    report = (
                        formatting.color(formatting.bold("Log action: "), formatting.color.RED)
                        + action
                        + " || "
                        + editor
                        + " deleted revision "
                        + revID
                        + " of page "
                        + pageLink
                        + " "
                        + comment[:200]
                    )
                elif subType == "DELETE_REDIR":
                    report = (
                        formatting.color(formatting.bold("Log action: "), formatting.color.RED)
                        + action
                        + " || "
                        + editor
                        + " deleted "
                        + pageLink
                        + " "
                        + comment[:200]
                    )
                else:
                    report = (
                        formatting.color(formatting.bold("Log action: "), formatting.color.RED)
                        + action
                        + " || "
                        + editor
                        + " "
                        + subType
                        + "ed "
                        + pageLink
                        + " "
                        + comment[:200]
                    )
            elif action == "PROTECT":
                if subType == "MODIFY":
                    description = change["log_params"]["description"]
                    report = (
                        formatting.color(formatting.bold("Log action: "), formatting.color.RED)
                        + action
                        + " || "
                        + editor
                        + " changed protection for "
                        + pageLink
                        + " "
                        + description
                        + " "
                        + comment[:200]
                    )
                elif subType == "UNPROTECT":
                    report = (
                        formatting.color(formatting.bold("Log action: "), formatting.color.RED)
                        + action
                        + " || "
                        + editor
                        + " removed protection for "
                        + pageLink
                        + " "
                        + comment[:200]
                    )
                else:
                    description = change["log_params"]["description"]
                    report = (
                        formatting.color(formatting.bold("Log action: "), formatting.color.RED)
                        + action
                        + " || "
                        + editor
                        + " "
                        + subType
                        + "ed "
                        + pageLink
                        + " "
                        + description
                        + " "
                        + comment[:200]
                    )
            else:
                report = (
                    formatting.color(formatting.bold("Log action: "), formatting.color.RED)
                    + action
                    + " || "
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
                    formatting.color(title, formatting.color.GREEN)
                    + " was edited by "
                    + formatting.color(formatting.bold(editor), formatting.color.BLUE)
                    + " "
                    + chDiff
                    + " "
                    + formatting.color(chComment, formatting.color.GRAY)
                )
            elif change["type"] == "new":
                report = (
                    formatting.color(title, formatting.color.GREEN)
                    + " was created by "
                    + formatting.color(formatting.bold(editor), formatting.color.BLUE)
                    + " "
                    + chDiff
                    + " "
                    + formatting.color(chComment, formatting.color.GRAY)
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
        """SELECT channel FROM rc_feed WHERE project=? and channel=?;""",
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
        c.execute("""INSERT INTO rc_feed VALUES(?, ?);""", (project, channel))
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
            """DELETE FROM rc_feed WHERE project=? and channel=?;""", (project, channel)
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
            "You are not authorized to start the Recent Changes feed in this channel."
        )
        return response

    if checkchannel(trigger.group(4), trigger.sender):
        response = (
            "I'm already reporting Recent Changes for "
            + trigger.group(4)
            + " in this channel."
        )
        return response

    if add_channel(trigger.group(4), trigger.sender):
        response = (
            "I will report Recent Changes on " + trigger.group(4) + " in this channel."
        )
    else:
        response = "An unknown error occurred during addition to database."

    return response


def stop(trigger):
    if not cabalutil.check_feedadmin(trigger.account, trigger.sender):
        response = (
            "You are not authorized to stop the Recent Changes feed in this channel."
        )
        return response

    if not checkchannel(trigger.group(4), trigger.sender):
        response = "I'm not reporting Recent Changes in this channel."
        return response

    if del_channel(trigger.group(4), trigger.sender):
        response = "Recent Changes for " + trigger.group(4) + " have been stopped."
    else:
        response = "An unknown error occurred during removal from the database."

    return response
