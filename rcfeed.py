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
            space = u"\u200B"
            editor = change["user"][:2] + space + change["user"][2:]
            comment = str(change["comment"]).replace("\n", "")

            if action in no_action:
                return
            elif action == "BLOCK":
                if subType == "UNBLOCK":
                    report = (
                        "Log action: "
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
                        "Log action: "
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
                    "Log action: "
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
                    "Log action: "
                    + action
                    + " || New user "
                    + pageLink
                    + " was created."
                )
            elif action == "RIGHTS":
                newGroups = change["log_params"]["newgroups"]
                oldGroups = change["log_params"]["oldgroups"]
                report = (
                    "Log action: "
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
                        "Log action: "
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
                        "Log action: "
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
                        "Log action: "
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
                        "Log action: "
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
                        "Log action: "
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
                        "Log action: "
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
                        "Log action: "
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
                    "Log action: "
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
            space = u"\u200B"
            editor = editor[:2] + space + editor[2:]

            if change["type"] == "edit":
                report = (
                    "\x02"
                    + title
                    + "\x02 was edited by \x02"
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
                    + "\x02 was created by \x02"
                    + editor
                    + "\x02 "
                    + chDiff
                    + " "
                    + chComment
                )

        if report is not None:
            for chan in channel:
                if cabalutil.check_hush(chan[0]) is True:
                    return
                else:
                    bot.say(report, chan[0])