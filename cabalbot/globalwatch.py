import cabalutil
import sqlite3


def check(change):

    try:
        nspace, title = str(change["title"]).split(":", 1)
    except ValueError:
        title = str(change["title"])

    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    stalk = c.execute(
        """SELECT title FROM global_watch WHERE title=?;""", (title,)
    ).fetchall()

    db.close()

    if len(stalk) > 0:
        return True
    else:
        return False

def report(bot, change):
    """title / namespace / nick / channel / notify"""

    proj = change["wiki"]
    fulltitle = str(change["title"])
    chRev = str(change["revision"]["new"])
    chURL = change["server_url"]
    chDiff = chURL + "/w/index.php?diff=" + chRev
    chComment = change["comment"]
    chNamespace = str(change["namespace"])
    editor = change["user"]
    space = u"\u200B"
    editor = editor[:2] + space + editor[2:]

    try:
        nmspace, title = fulltitle.split(":", 1)
    except ValueError:
        title = fulltitle

    check = None

    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    try:
        check = c.execute(
            """SELECT * FROM global_watch where title=?;""", (title,)
        ).fetchall()
    except:
        return

    if check is not None:
        channels = []

        for record in check:
            (
                target_title,
                target_namespace,
                target_nick,
                target_channel,
                target_notify,
            ) = record
            if target_namespace == chNamespace:
                channels.append(target_channel)
        channels = list(dict.fromkeys(channels))  # Collapse duplicate channels

        for chan in channels:
            nicks = ""
            pgNicks = c.execute(
                """SELECT nick from global_watch where title=? and namespace=? and channel=? and notify="on";""",
                (title, chNamespace, chan),
            ).fetchall()

            if len(pgNicks) > 0:
                for nick in pgNicks:
                    if nicks == "":
                        nicks = nick[0]
                    else:
                        nicks = nick[0] + " " + nicks
                if change["type"] == "edit":
                    newReport = (
                        nicks
                        + ": \x02"
                        + fulltitle
                        + "\x02 on "
                        + proj
                        + " was edited by \x02"
                        + editor
                        + "\x02 "
                        + chDiff
                        + " "
                        + chComment
                    )
                elif change["type"] == "create":
                    newReport = (
                        nicks
                        + ": \x02"
                        + fulltitle
                        + "\x02 on "
                        + proj
                        + " was created by \x02"
                        + editor
                        + "\x02 "
                        + chDiff
                        + " "
                        + chComment
                    )
            else:
                if change["type"] == "edit":
                    newReport = (
                        "\x02"
                        + fulltitle
                        + "\x02 on "
                        + proj
                        + " was edited by \x02"
                        + editor
                        + "\x02 "
                        + chDiff
                        + " "
                        + chComment
                    )
                elif change["type"] == "create":
                    newReport = (
                        "\x02"
                        + fulltitle
                        + "\x02 on "
                        + proj
                        + " was created by \x02"
                        + editor
                        + "\x02 "
                        + chDiff
                        + " "
                        + chComment
                    )

            if cabalutil.check_hush(chan) is True:
                continue
            else:
                bot.say(newReport, chan)

        db.close()
    else:
        db.close()


def globalWatcherAdd(msg, nick, chan):
    # !globalwatch add namespaceid title
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    action, nspace, title = msg.split(" ", 2)

    checkExisting = c.execute(
        """SELECT * FROM global_watch WHERE title=? AND namespace=? AND nick=? AND channel=?;""",
        (title, nspace, nick, chan),
    ).fetchone()

    if checkExisting is None:
        try:
            c.execute(
                """INSERT INTO global_watch VALUES(?, ?, ?, ?, ?);""",
                (title, nspace, nick, chan, "off"),
            )
            db.commit()
        except Exception as e:
            response = (
                "Ugh... Something blew up adding the page to the table: "
                + str(e)
                + ". "
                + bot.settings.core.owner
                + " help me."
            )
            db.close()
            return response
        check = c.execute(
            """SELECT * FROM global_watch WHERE title=? AND namespace=? AND nick=? AND channel=?;""",
            (title, nspace, nick, chan),
        ).fetchone()

        page, space, user, channel, ping = check

        response = (
            user
            + ": I will report changes to "
            + page
            + " in namespace "
            + space
            + " on all projects with no ping."
        )
    else:
        response = (
            nick
            + ": you are already globally watching "
            + nspace
            + ":"
            + page
            + " in this channel."
        )

    db.close()
    return response


def globalWatcherDel(msg, nick, chan):
    # !globalwatch del namespaceid title
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    action, nspace, title = msg.split(" ", 2)

    checkExisting = c.execute(
        """SELECT * FROM global_watch WHERE title=? AND namespace=? AND nick=? AND channel=?;""",
        (title, nspace, nick, chan),
    ).fetchone()

    if checkExisting is not None:
        try:
            c.execute(
                """DELETE FROM global_watch WHERE title=? AND namespace=? AND nick=? AND channel=?;""",
                (title, nspace, nick, chan),
            )
            db.commit()
        except Exception as e:
            response = str(e)
            db.close()
            return response

        check = c.execute(
            """SELECT * FROM global_watch WHERE title=? AND namespace=? AND nick=? AND channel=?;""",
            (title, nspace, nick, chan),
        ).fetchone()

        if check is None:
            response = (
                nick
                + ": I will no longer report changes to "
                + title
                + " in namespace "
                + nspace
                + "."
            )
        else:
            response = "Confirmation failed. Pinging " + bot.settings.core.owner
    else:
        response = (
            nick
            + ": you are not globally watching "
            + nspace
            + ":"
            + title
            + " in this channel."
        )

    db.close()
    return response


def globalWatcherPing(msg, nick, chan):
    # !globalwatch ping on namespaceid title
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    action, switch, nspace, title = msg.split(" ", 3)
    switch = switch.lower()

    if switch == "on" or switch == "off":
        c.execute(
            """UPDATE global_watch SET notify=? WHERE title=? AND namespace=? AND nick=? AND channel=?;""",
            (switch, title, nspace, nick, chan),
        ).fetchone()
        db.commit()
        response = (
            "Ping set to "
            + switch
            + " for "
            + title
            + " in namespace "
            + nspace
            + " in this channel."
        )
    else:
        response = "Malformed command! Try: !globalwatch ping {on/off} namespaceID The page you want"

    db.close()

    return response