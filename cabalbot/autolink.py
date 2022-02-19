import sqlite3
import cabalutil


def checklang(channel):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    check = c.execute(
        """SELECT * FROM channel_lang WHERE channel=?;""", (channel,)
    ).fetchall()
    db.close()

    if len(check) > 0:
        return True
    else:
        return False


def addlang(channel, project, url=""):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    c.execute("""INSERT INTO channel_lang VALUES(?, ?, ?);""", (channel, project, url))
    db.commit()

    check = c.execute(
        """SELECT * FROM channel_lang WHERE channel=?;""", (channel,)
    ).fetchone()
    db.close()

    if len(check) > 0:
        return True


def rmvlang(channel):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    c.execute("""DELETE FROM channel_lang WHERE channel=?;""", (channel,))
    db.commit()
    check = c.execute(
        """SELECT * FROM channel_lang WHERE channel=?;""", (channel,)
    ).fetchone()
    db.close()

    if check is None:
        return True


def getlang(channel):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    result = c.execute(
        """SELECT url FROM channel_lang WHERE channel=?;""", (channel,)
    ).fetchone()
    db.close()

    if result is None:
        return result
    else:
        return result[0]


def ignorenick(account, admin):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    c.execute("""INSERT INTO ignore_nicks VALUES(?,?);""", (account, admin))
    db.commit()

    verify = c.execute(
        """SELECT * FROM ignore_nicks WHERE target=?;""", (account,)
    ).fetchall()
    db.close()

    if len(verify) > 0:
        return True
    else:
        return False


def unignorenick(account):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    c.execute("""DELETE FROM ignore_nicks WHERE target=?;""", (account,))
    db.commit()

    verify = c.execute(
        """SELECT * FROM ignore_nicks WHERE target=?;""", (account,)
    ).fetchone()
    db.close()

    if verify is None:
        return True
    else:
        return False
