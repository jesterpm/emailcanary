import uuid, datetime, time
import email
import re

class Canary:
	def __init__(self, db, smtp, fromaddress):
		self.db = db
		self.smtp = smtp
		self.fromaddress = fromaddress

	def chirp(self, list, expectedreceipients):
		uuid = uuid.uuid4()
		now = datetime.datetime.now()

		self.send(list, now, uuid)
		for dest in expectedreceipients:
			self.db.ping(dest, now, uuid)

	def echo(self, receipient, msg):
		uuid = re.match('Canary Email (.+)', msg['Subject']).group(1)
		now = datetime.datetime.now()

		self.db.pong(receipient, now, uuid)


	def send(self, dest, date, uuid):
		msg = email.message.Message()
		msg['From'] = self.fromaddress
		msg['To'] = dest
		msg['Subject'] = "Canary Email " + str(uuid)
		msg['Date'] = email.utils.formatdate(time.mktime(date.timetuple()))

		self.smtp.sendmail(self.fromaddress, dest, msg.as_string())