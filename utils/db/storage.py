import sqlite3 as lite


class DatabaseManager(object):

    def __init__(self, path):
        self.conn = lite.connect(path)
        self.conn.execute('pragma foreign_keys = on')
        self.conn.commit()
        self.cur = self.conn.cursor()



    def create_tables(self):
        self.query('CREATE TABLE IF NOT EXISTS users (idx INTEGER PRIMARY KEY, userid TEXT, fullname TEXT, username TEXT, regdate TEXT DEFAULT CURRENT_TIMESTAMP, subscribed INTEGER DEFAULT 0)')
        self.query("CREATE TABLE IF NOT EXISTS channel (idx INTEGER PRIMARY KEY, chid TEXT, title TEXT, link TEXT)")
        self.query("CREATE TABLE IF NOT EXISTS bulk_messages (idx INTEGER PRIMARY KEY, content TEXT, type TEXT, status INTEGER DEFAULT 0, date TEXT DEFAULT CURRENT_TIMESTAMP)")
        # New table to store message settings
        self.query("CREATE TABLE IF NOT EXISTS external_links (idx INTEGER PRIMARY KEY, title TEXT, link TEXT)")
        self.query("CREATE TABLE IF NOT EXISTS message_settings (key TEXT PRIMARY KEY, content TEXT)")

    def query(self, arg, values=None):
        if values == None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        self.conn.commit()

    def fetchone(self, arg, values=None):
        if values == None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchone()

    def fetchall(self, arg, values=None):
        if values == None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchall()

    def add_bulk_message(self, content, type):
        self.query("INSERT INTO bulk_messages (content, type) VALUES (?, ?)", (content, type))
        return self.cur.lastrowid

    def update_bulk_message_status(self, idx, status):
        self.query("UPDATE bulk_messages SET status = ? WHERE idx = ?", (status, idx))

    def get_bulk_message_status(self, idx):
        return self.fetchone("SELECT status FROM bulk_messages WHERE idx = ?", (idx,))

    def get_all_users(self):
        return self.fetchall("SELECT userid FROM users")

    def update_message_setting(self, key, content):
        if self.fetchone("SELECT key FROM message_settings WHERE key = ?", (key,)):
            self.query("UPDATE message_settings SET content = ? WHERE key = ?", (content, key))
        else:
            self.query("INSERT INTO message_settings (key, content) VALUES (?, ?)", (key, content))

    def get_message_setting(self, key):
        return self.fetchone("SELECT content FROM message_settings WHERE key = ?", (key,))

    def __del__(self):
        self.conn.close()


'''
users: idx, userid, fullname, username, regdate, banned
exams: idx, code, title, about, num_questions, correct, running
submissions: idx, exid, userid, date, corr
channel: idx, chid, title, username
'''