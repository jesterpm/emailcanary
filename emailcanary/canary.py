import uuid, datetime, time
import email.message
import re
from . import emailutils

class Canary:
    def __init__(self, db, smtp, fromaddress):
        self.db = db
        self.smtp = smtp
        self.fromaddress = fromaddress

    def chirp(self, listAddress):
        chirpUUID = str(uuid.uuid4())
        now = datetime.datetime.now()

        receipients = self.db.get_recipients_for_list(listAddress)
        if len(receipients) == 0:
            raise Exception("No receipients for listAddress '%s'", (listAddress,))

        self.send(listAddress, now, chirpUUID)
        for dest in receipients:
            self.db.ping(listAddress, dest, now, chirpUUID)

    def check(self, listAddress):
        '''Check for messages from listAddress and return a list of missing chirps'''
        accounts = self.db.get_accounts(listAddress)
        if len(accounts) == 0:
            raise Exception("No receipients for listAddress '%s'", (listAddress,))
        result = []
        for (listAddress, address, imapserver, password, mute) in accounts:
            mail = emailutils.get_imap(imapserver, address, password)
            these_subjects = []
            for uid in emailutils.get_mail_uids(mail):
                message = emailutils.get_message(mail, uid)
                if message is not None and self.processMessage(address, message):
                    emailutils.delete_message(mail, uid)
            emailutils.close(mail)
            if time.time() > mute:
                result.extend(self.db.get_missing_pongs(listAddress, address))
        return result

    def processMessage(self, receipient, msg):
        match = re.match('.*Canary Email (.+)', msg['Subject'])
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
