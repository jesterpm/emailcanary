import uuid, datetime, time
import email, emailutils
import re

class Canary:
	def __init__(self, db, smtp, fromaddress):
		self.db = db
		self.smtp = smtp
		self.fromaddress = fromaddress

	def chirp(self, listAddress):
		chirpUUID = str(uuid.uuid4())
		now = datetime.datetime.now()

		self.send(listAddress, now, chirpUUID)
		for dest in self.db.get_recipients_for_list(listAddress):
			self.db.ping(dest, now, chirpUUID)

	def check(self, listAddress):
		for (listAddress, address, imapserver, password) in self.db.get_accounts(listAddress):
			mail = emailutils.get_imap(imapserver, address, password)
			these_subjects = []
			for uid in emailutils.get_mail_uids(mail):
				message = emailutils.get_message(mail, uid)
				if self.processMessage(address, message):
					emailutils.delete_message(mail, uid)
			emailutils.close(mail)

	def processMessage(self, receipient, msg):
		match = re.match('Canary Email (.+)', msg['Subject'])
		if match:
			chirpUUID = match.group(1)
			now = datetime.datetime.now()
			self.db.pong(receipient, now, chirpUUID)
			return True
		return False


	def send(self, dest, date, chirpUUID):
		msg = email.message.Message()
		msg['From'] = self.fromaddress
		msg['To'] = dest
		msg['Subject'] = "Canary Email " + chirpUUID
		msg['Date'] = email.utils.formatdate(time.mktime(date.timetuple()))

		self.smtp.sendmail(self.fromaddress, dest, msg.as_string())
