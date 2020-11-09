import sqlite3
import os

class DBHelper:

    # take database name and creates database connection
    def __init__(self, dbname='voice.sqlite'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    # creates a new table called voice. has 2 columns
    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS voices (chat_id text," \
                                                 "voice_id text)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_voice(self, chat_id, voice_id):
        # if there is no user yet, create new:
        stmt = "SELECT voice_id FROM voices WHERE chat_id = (?)"
        check = [ x[0] for x in self.conn.execute(stmt,(chat_id,))]

        if (check == []):
            stmt = "INSERT INTO voices (chat_id, voice_id) VALUES (?, ?)"
            args = (chat_id, voice_id)
            self.conn.execute(stmt, args)
            self.conn.commit()
        # if the user already used our bot
        else:
            stmt = """UPDATE voices SET voice_id = ? WHERE chat_id = ?"""
            args = (voice_id, chat_id)
            self.conn.execute(stmt, args)
            self.conn.commit()
            # delete previous file
            os.remove("input\\{}.wav".format(check[-1]))


    def delete_voice(self, chat_id):
        stmt = "DELETE FROM voices WHERE chat_id = (?)"
        args = (chat_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_voice(self, chat_id):
        stmt = "SELECT voice_id FROM voices WHERE chat_id = (?)"
        return [ x[0] for x in self.conn.execute(stmt,(chat_id,))]
