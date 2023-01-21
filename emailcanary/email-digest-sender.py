import smtplib
from email import message
from . import emailutils

PASSWORD="secret"
ACCOUNTS = [('mail.example.com', 'email@example.com', PASSWORD)]
DESTINATION="other@example.com"

youve_got_mail = False
all_subjects = {}

for account in ACCOUNTS:
    mail = emailutils.get_imap(account[0], account[1], account[2])
    these_subjects = []
    for uid in emailutils.get_mail_uids(mail):
        message = emailutils.get_message(mail, uid)
        these_subjects.append(message['subject'])
        youve_got_mail = True
    all_subjects[account[1]] = these_subjects


if youve_got_mail:
    msg = ""
    for account in all_subjects:
        msg = msg + "# Messages for %s\n" % account
        for subject in all_subjects[account]:
            msg = msg + " * %s\n" % subject
        msg = msg + "\n"

    digest_message = message.Message()
    digest_message.set_payload(msg)
    digest_message['From'] = DESTINATION
    digest_message['To'] = DESTINATION
    digest_message['Subject'] = "Email Digest"

    s = smtplib.SMTP_SSL('localhost', 2465)
    s.sendmail(DESTINATION, DESTINATION, digest_message.as_string())
    s.quit()
