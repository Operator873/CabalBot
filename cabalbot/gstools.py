import sqlite3
import cabalutil
from sopel import formatting
from urllib.parse import urlparse

def report(bot, change):

    gs = change["user"]
    gs_list = None

    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    gs_list = c.execute(
        """SELECT account FROM globalsysops WHERE account=?;""", (gs,)
    ).fetchall()

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

    if len(gs_list) > 0:

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
                "Log action by "
                + formatting.color(editor, formatting.colors.GREEN)
                + ": "
                + formatting.color(formatting.bold(action), formatting.colors.RED)
                + " || "
                + pageLink
                + " was "
                + actionType
                + "ed || Flags: "
                + flags
                + " || Duration: "
                + duration
                + " || Comment: "
                + comment[:200]
            )
        elif action == "ABUSEFILTER":
            report = action + " activated by " + editor + " " + pageLink
        elif action == "MOVE":
            report = (
                "Log action by "
                + formatting.color(editor, formatting.colors.GREEN)
                + ": "
                + formatting.color(formatting.bold(action), formatting.colors.RED)
                + " || "
                + editor
                + " moved "
                + pageLink
                + " "
                + comment[:200]
            )
        else:
            report = (
                "Log action by "
                + formatting.color(editor, formatting.colors.GREEN)
                + ": "
                + formatting.color(formatting.bold(action), formatting.colors.RED)
                + " || "
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
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    check = c.execute(
        """SELECT * FROM GSwikis WHERE project=?;""", (project,)
    ).fetchall()

    db.close()

    if len(check) > 0:
        return True
    else:
        return False


def addGS(trigger):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    check = c.execute(
        """SELECT account FROM globalsysops WHERE nick=?;""", (trigger.group(3),)
    ).fetchall()

    if len(check) == 0:
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

        response = (
            "Wikipedia account "
            + trigger.group(4)
            + " is now known by IRC nick(s): "
            + nicks
        )
    else:
        response = (
            trigger.group(3)
            + " is already associated with "
            + trigger.group(4)
        )

    db.close()
    return response



def delGS(trigger):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()
    c.execute("""DELETE FROM globalsysops WHERE account=?;""", (trigger.group(3),))
    db.commit()

    check_work = c.execute(
        """SELECT nick FROM globalsysops WHERE account=?;""", (trigger.group(3),)
    ).fetchall()
    db.close()

    if len(check_work) == 0:
        response = (
            "All nicks for "
            + trigger.group(3)
            + " have been purged."
        )
    else:
        response = "Something wonky happened during delete verification."

    return response


def on_irc(wiki):
    response = {
        "ok": True
    }
    if not check(wiki):
        response["ok"] = False
        response["msg"] = (
            "I don't know "
            + wiki
            + "... Pinging Operator873."
        )
        return response

    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    wikidata = c.execute(
        """SELECT * FROM GSwikis WHERE project=?;""", (wiki,)
    ).fetchone()

    db.close()

    if wikidata is None:
        response["ok"] = False
        response["msg"] = "Something borked while gathering wiki data."
        return response

    proj, apiurl, csdcat = wikidata
    urlpre = urlparse(apiurl)
    response["data"] = []

    query = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": csdcat
    }

    d = cabalutil.xmit(urlpre.netloc, query, "get")

    for item in d["query"]["categorymembers"]:
        entry = (
            "https://"
            + urlpre.netloc
            + "/wiki/"
            + item["title"]
        ).replace(" ", "_")

        response["data"].append(entry)

    if 'continue' in d:
        response["more"] = True
    else:
        response["more"] = False

    return response


def add_wiki(proj, api, cat):
    if not check(proj):
        db = sqlite3.connect(cabalutil.getdb())
        c = db.cursor()
        c.execute(
            """INSERT INTO GSwikis VALUES(?, ?, ?);""", (proj, api, cat)
        )

        db.commit()
        db.close()

        response = (
            proj
            + " was saved with API: "
            + api
            + " and category: "
            + cat
        )
    else:
        response = "I already know " + proj

    return response


def del_wiki(proj):
    if check(proj):
        db = sqlite3.connect(cabalutil.getdb())
        c = db.cursor()

        c.execute(
            """DELETE FROM GSwikis WHERE project=?;""", (proj,)
        )

        db.commit()
        db.close()

        response = (proj + " was successfully deleted from the database.")
    else:
        response = "I don't know " + proj

    return response

