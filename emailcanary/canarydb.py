import sqlite3
from datetime import datetime

class CanaryDB:
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

        # Create Tables if necessary
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS pings (listAddress, address, uuid, timesent timestamp, timereceived timestamp)")
        cursor.execute("CREATE TABLE IF NOT EXISTS accounts (list, address, imapserver, password, mute)")

    def close(self):
        self.conn.close()

    def add_account(self, listAddress, address, imapserver, password):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO accounts (list, address, imapserver, password, mute) VALUES (?, ?, ?, ?, 0)", \
            (listAddress, address, imapserver, password))
        self.conn.commit()

    def remove_account(self, listAddress, address):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM accounts WHERE list=? AND address=?", (listAddress, address))
        self.conn.commit()

    def mute_account(self, listAddress, address, until):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE accounts SET mute=? WHERE list=? AND address=?", (until, listAddress, address))
        self.conn.commit()

    def get_accounts(self, listAddress = None):
        cursor = self.conn.cursor()
        if listAddress:
            cursor.execute("SELECT list, address, imapserver, password, mute FROM accounts WHERE list=?", (listAddress,));
        else:
            cursor.execute("SELECT list, address, imapserver, password, mute FROM accounts");
        results = list()
        for row in cursor:
            listAddress = row[0]
            address = row[1]
            imapserver = row[2]
            password = row[3]
            mute = row[4]
            results.append((listAddress, address, imapserver, password, mute))
        return results

    def get_recipients_for_list(self, listAddress):
        cursor = self.conn.cursor()
        cursor.execute("SELECT address FROM accounts WHERE list=?", (listAddress,));
        results = list()
        for row in cursor:
            results.append(row[0])
        return results

    def ping(self, listAddress, address, time, uuid):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO pings (listAddress, address, timesent, uuid) VALUES (?, ?, ?, ?)", \
            (listAddress, address, time, uuid))
        self.conn.commit()

    def pong(self, address, time, uuid):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE pings SET timereceived=? WHERE address=? AND uuid=?", \
            (time, address, uuid))
        self.conn.commit()

    def get_missing_pongs(self, listAddress = None, address = None):
        '''Return a list of tupls of missing pongs.
           Each tupl contains (listAddress, uuid, address, time since send)'''
        cursor = self.conn.cursor()
        if listAddress and address:
            cursor.execute("SELECT listAddress, uuid, address, timesent FROM pings WHERE timereceived IS NULL AND listAddress = ? AND address = ?", (listAddress, address,));
        elif listAddress:
            cursor.execute("SELECT listAddress, uuid, address, timesent FROM pings WHERE timereceived IS NULL AND listAddress = ?", (listAddress,));
        else:
            cursor.execute("SELECT listAddress, uuid, address, timesent FROM pings WHERE timereceived IS NULL");
        now = datetime.now()
        results = list()
        for row in cursor:
            listAddress = row[0]
            uuid = row[1]
            address = row[2]
            delta = now - row[3]
            results.append((listAddress, uuid, address, delta))
        return results
