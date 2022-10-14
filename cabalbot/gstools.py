import cabalutil
from sopel import formatting
from urllib.parse import urlparse


def report(bot, change):
    gs = change["user"]
    query = f"SELECT account FROM globalsysops WHERE account='{gs}';"
    gs_list = cabalutil.do_sqlite(query, 'all')

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
    query = f"SELECT * FROM GSwikis WHERE project='{project}';"
    check = cabalutil.do_sqlite(query, 'all')

    if len(check) > 0:
        return True
    else:
        return False


def addGS(trigger):
    query = f"SELECT account FROM globalsysops WHERE nick='{trigger.group(3)}';"
    check = cabalutil.do_sqlite(query, 'all')

    if len(check) == 0:
        insert_query = f"INSERT INTO globalsysops VALUES('{trigger.group(3)}', '{trigger.group(4)}');"
        if not cabalutil.do_sqlite(insert_query, 'act'):
            return "Failure occurred while writing to database!"

        nick_query = f"SELECT nick FROM globalsysops where account='{trigger.group(4)}';"
        nick_check = cabalutil.do_sqlite(nick_query, 'all')

        nicks = ""
        for nick in nick_check:
            if nicks == "":
                nicks = nick[0]
            else:
                nicks = nicks + " " + nick[0]

        response = f"Wikipedia account {trigger.group(4)} is no known by IRC nick(s): {nicks}"
    else:
        response = f"{trigger.group(3)} is already associated with {trigger.group(4)}"

    return response



def delGS(trigger):
    delete = f"DELETE FROM globalsysops WHERE account='{trigger.group(3)}';"
    cabalutil.do_sqlite(delete, 'act')

    check_work = cabalutil.do_sqlite(
        f"SELECT nick FROM globalsysops WHERE account='{trigger.group(3)}';",
        'all'
    )

    if len(check_work) == 0:
        response = f"All nicks for {trigger.group(3)} have been purged."
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
            + "."
        )
        return response

    wikidata = cabalutil.do_sqlite(
        f"SELECT * FROM GSwikis WHERE project={wiki};",
        'one'
    )

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

    if len(d["query"]["categorymembers"]) > 0:
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
    else:
        response = {
            "ok": False,
            "msg": "There are currently no pages in the CSD category."
        }

    return response


def add_wiki(proj, api, cat):
    if not check(proj):
        if cabalutil.do_sqlite(
            f"INSERT INTO GSwikis VALUES('{proj}', '{api}', '{cat}');",
            'act'
        ):
            response = f"{proj} was saved! API: {api} Cat: {cat}"
        else:
            response = "An error occurred while editing the database."
    else:
        response = f"I already know {proj}"

    return response


def del_wiki(proj):
    if check(proj):
        if cabalutil.do_sqlite(
            f"DELETE FROM GSwikis WHERE project='{proj}';",
            'act'
        ):
            response = f"{proj} was successfully deleted from the database."
        else:
            response = "An error occurred while editing the database."
    else:
        response = f"I don't know {proj}"

    return response

