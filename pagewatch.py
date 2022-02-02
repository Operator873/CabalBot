import cabalutil
import sqlite3
import re


def check(change):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    exists = c.execute(
        """SELECT name FROM sqlite_master WHERE type='table' AND name=?;""", (proj,)
    ).fetchone()

    db.close()

    if exists is not None and len(exists) > 0:
        return True
    else:
        return False

def checkcss(change):

    if (
        re.search(r".*\.css$", change["title"]) or
        re.search(r".*\.js$", change["title"])
    ):
        return True
    else:
        return False

def report(bot, change):

    proj = change["wiki"]
    title = str(change["title"])
    chRev = str(change["revision"]["new"])
    chURL = change["server_url"]
    chDiff = chURL + "/w/index.php?diff=" + chRev
    chComment = change["comment"]
    editor = change["user"]
    space = u"\u200B"
    editor = editor[:2] + space + editor[2:]
    check = None

    # Band aid SQL injection prevention. Not a pretty fix
    # This will always only be a wiki name ie enwiki, ptwiki, etc
    # The only source is the EventStream so can be considered "safe"
    checkquery = """SELECT * FROM %s where page=?;""" % proj
    nickquery = (
        """SELECT nick from %s where page=? and channel=? and notify="on";""" % proj
    )

    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    try:
        check = c.execute(checkquery, (title,)).fetchall()
    except:
        return

    if check is not None:
        channels = []

        for record in check:
            dbPage, dbNick, dbChan, notify = record
            channels.append(dbChan)
        channels = list(dict.fromkeys(channels))  # Collapse duplicate channels

        for chan in channels:
            nicks = ""
            pgNicks = c.execute(nickquery, (title, chan)).fetchall()

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
                        + title
                        + "\x02 on "
                        + proj
                        + " was edited by \x02"
                        + editor
                        + "\x02 "
                        + chDiff
                        + " "
                        + chComment
                    )
                elif change["type"] == "new":
                    newReport = (
                        nicks
                        + ": \x02"
                        + title
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
                        + title
                        + "\x02 on "
                        + proj
                        + " was edited by \x02"
                        + editor
                        + "\x02 "
                        + chDiff
                        + " "
                        + chComment
                    )
                elif change["type"] == "new":
                    newReport = (
                        "\x02"
                        + title
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


def watcherAdd(msg, nick, chan):
    checkquery = """SELECT count(*) FROM sqlite_master WHERE type="table" AND name=?;"""
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    action, project, page = msg.split(" ", 2)
    project = project.replace(";", " ")  # 7/11 Special to avoid injection

    checkTable = c.execute(checkquery, (project,)).fetchone()
    if checkTable[0] == 0:
        try:
            c.execute(
                """CREATE TABLE %s (page TEXT, nick TEXT, channel TEXT, notify TEXT);"""
                % project
            )
            db.commit()
        except Exception as e:
            response = (
                "Ugh... Something blew up creating the table. "
                + bot.settings.core.owner
                + " help me. "
                + str(e)
            )
            db.close()
            return response

        # Check to see if we have the table
        check = c.execute(checkquery, (project,)).fetchone()
        if check[0] == 0:
            response = (
                "Ugh... Something blew up finding the new table: ("
                + check
                + ") "
                + bot.settings.core.owner
                + " help me."
            )
            db.close()
            return response

    pageExists = c.execute(
        """SELECT * from %s WHERE page="%s" AND nick="%s" AND channel="%s";"""
        % (project, page, nick, chan)
    ).fetchone()
    if pageExists is None:
        try:
            c.execute(
                """INSERT INTO %s VALUES("%s", "%s", "%s", "off");"""
                % (project, page, nick, chan)
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
            """SELECT * FROM %s WHERE page="%s" AND nick="%s" AND channel="%s";"""
            % (project, page, nick, chan)
        ).fetchone()
        rePage, reNick, reChan, reNotify = check
        response = (
            nick
            + ": I will report changes to "
            + page
            + " on "
            + project
            + " with no ping."
        )
    else:
        response = (
            nick
            + ": you are already watching "
            + page
            + " on "
            + project
            + " in this channel."
        )

    db.close()
    return response


def watcherDel(msg, nick, chan):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    action, project, page = msg.split(" ", 2)

    checkPage = c.execute(
        """SELECT * FROM %s WHERE page="%s" AND nick="%s" AND channel="%s";"""
        % (project, page, nick, chan)
    ).fetchone()
    if checkPage is not None:
        try:
            c.execute(
                """DELETE FROM %s WHERE page="%s" AND nick="%s" AND channel="%s";"""
                % (project, page, nick, chan)
            )
            db.commit()
            response = (
                "%s: I will no longer report changes to %s on %s in this channel for you"
                % (nick, page, project)
            )
        except:
            response = (
                "Ugh... Something blew up. " + bot.settings.core.owner + " help me."
            )
    else:
        response = (
            "%s: it doesn't look like I'm reporting changes to %s on %s in this channel for you."
            % (nick, page, project)
        )

    db.close()
    return response


def watcherPing(msg, nick, chan):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    action, switch, project, page = msg.split(" ", 3)

    if switch.lower() == "on" or switch.lower() == "off":
        c.execute(
            """UPDATE %s set notify="%s" where page="%s" and nick="%s" and channel="%s";"""
            % (project, switch, page, nick, chan)
        )
        db.commit()
        response = (
            "Ping set to "
            + switch
            + " for "
            + page
            + " on "
            + project
            + " in this channel."
        )
    else:
        response = (
            "Malformed command! Try: !watch ping {on/off} project The page you want"
        )

    db.close()

    return response


def cssjs(bot, change):
    proj = change["wiki"]
    title = str(change["title"])
    chRev = str(change["revision"]["new"])
    chURL = change["server_url"]
    chDiff = chURL + "/w/index.php?diff=" + chRev + "&safemode=1"
    chComment = change["comment"]
    editor = change["user"]
    space = u"\u200B"
    editor = editor[:2] + space + editor[2:]

    bot.say(
        "\x02"
        + title
        + "\x02 on "
        + proj
        + " was edited by \x02"
        + editor
        + "\x02 "
        + chDiff
        + " "
        + chComment,
        "#wikimedia-cssjs",
    )