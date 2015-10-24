import sqlite3
from datetime import datetime

class CanaryDB:
	def __init__(self, filename):
		self.conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

		# Create Tables if necessary
		cursor = self.conn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS pings (address, uuid, timesent timestamp, timereceived timestamp)")

	def close(self):
		self.conn.close()

	def ping(self, address, time, uuid):
		cursor = self.conn.cursor()
		cursor.execute("INSERT INTO pings (address, timesent, uuid) VALUES (?, ?, ?)", \
			(address, time, uuid))
		self.conn.commit()

	def pong(self, address, time, uuid):
		cursor = self.conn.cursor()
		cursor.execute("UPDATE pings SET timereceived=? WHERE address=? AND uuid=?", \
			(time, address, uuid))
		self.conn.commit()

	def get_missing_pongs(self):
		'''Return a list of tupls of missing pongs.
		   Each tupl contains (uuid, address, time since send)'''
		cursor = self.conn.cursor()
		cursor.execute("SELECT uuid, address, timesent FROM pings WHERE timereceived IS NULL");

		now = datetime.now()
		results = list()
		for row in cursor:
			uuid = row[0]
			address = row[1]
			delta = now - row[2]
			results.append((uuid, address, delta))

		return results
