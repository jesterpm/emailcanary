import sys
import imaplib, email

def get_imap(server, username, password):
    '''Connect and login via IMAP'''
    try:
        mail = imaplib.IMAP4_SSL(server)
        mail.login(username, password)
        return mail
    except Exception as e:
        sys.stderr.write("Error connecting to %s@%s: %s\n\n" % (username, server, str(e)))
        return None

def get_mail_uids(mail):
    '''Return a list of message UIDs in the inbox'''
    if mail is None:
        return []
    mail.select("inbox") # connect to inbox.
    result, data = mail.uid('search', None, "ALL") # search and return uids instead
    return data[0].split()

def get_message(mail, uid):
    '''Get a single email message object by UID'''
    if mail is None:
        return None
    result, data = mail.uid('fetch', uid, '(RFC822)')
    if result == 'OK':
        dat0 = data[0]
        if dat0 is None:
            return None
        else:
            raw_email = str(dat0[1])
            return email.message_from_string(raw_email)
    else:
        raise Exception("Bad response from server: %s" % (result))

def delete_message(mail, uid):
    if mail is None:
        return
    result = mail.uid('store', uid, '+FLAGS', '(\Deleted)')

def close(mail):
    if mail is None:
        return
    mail.expunge()
    mail.close()
    mail.logout()
