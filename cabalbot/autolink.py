import sqlite3
import cabalutil

def checklang(trigger):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    check = c.execute("""SELECT * FROM channel_lang WHERE channel=?;""", (trigger.sender,)).fetchall()
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

    check = c.execute("""SELECT * FROM channel_lang WHERE channel=?;""", (channel,)).fetchone()
    db.close()

    if len(check) > 0:
        return True


def rmvlang(channel):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    c.execute("""DELETE FROM channel_lang WHERE channel=?;""", (channel,))
    db.commit()
    check = c.execute("""SELECT * FROM channel_lang WHERE channel=?;""", (channel,)).fetchone()
    db.close()

    if len(check) == 0:
        return True

def getlang(channel):
    db = sqlite3.connect(cabalutil.getdb())
    c = db.cursor()

    result = c.execute("""SELECT url FROM channel_lang WHERE channel=?;""", (channel,)).fetchone()
    db.close()

    if result is None:
        return result
    else:
        return result[0]
