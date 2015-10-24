import imaplib, email

def get_imap(account):
	'''Connect and login via IMAP'''
	mail = imaplib.IMAP4_SSL(account[0])
	mail.login(account[1],  account[2])
	return mail

def get_mail_uids(mail):
	'''Return a list of message UIDs in the inbox'''
	mail.select("inbox") # connect to inbox.
	result, data = mail.uid('search', None, "ALL") # search and return uids instead
	return data[0].split()

def get_message(mail, uid):
	'''Get a single email message object by UID'''
	result, data = mail.uid('fetch', uid, '(RFC822)')
	raw_email = data[0][1]
	return email.message_from_string(raw_email)