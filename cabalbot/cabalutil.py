import sqlite3


def getdb():
    return "wiki.db"


def check_hush(channel):
    db = sqlite3.connect(getdb())
    c = db.cursor()

    hushCheck = c.execute(
        """SELECT * FROM hushchannels WHERE channel=?;""", (channel,)
    ).fetchall()

    db.close()

    if len(hushCheck) > 0:
        return True
    else:
        return False
