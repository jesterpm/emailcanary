import unittest
import mock
import tempfile, shutil
import datetime
import smtplib, email

from emailcanary import canary
from emailcanary import canarydb

FROM_ADDRESS = "from@example.com"
LIST_ADDRESS = "list@example.com"

USER_ADDRESS1 = "user1@example.com"
USER_ADDRESS2 = "user2@example.com"

SERVER = "mail.example.com"
PASSWORD = "secret"

class TestCanary(unittest.TestCase):
    def setUp(self):
        self.db = mock.Mock(canarydb.CanaryDB)
        self.smtp = mock.Mock(smtplib.SMTP_SSL)
        self.canary = canary.Canary(self.db, self.smtp, FROM_ADDRESS)
        canary.emailutils.get_imap = mock.Mock()
        canary.emailutils.get_message = mock.Mock()
        canary.emailutils.get_mail_uids = mock.Mock()
        canary.emailutils.delete_message = mock.Mock()
        canary.emailutils.close = mock.Mock()

    def tearDown(self):
        pass

    def testChirp(self):
        # Setup Mock
        self.db.get_recipients_for_list.return_value = [USER_ADDRESS1, USER_ADDRESS2]

        # Test chirp
        self.canary.chirp(LIST_ADDRESS)

        # Assert DB updated
        self.db.get_recipients_for_list.assert_called_with(LIST_ADDRESS)
        self.db.ping.assert_has_calls( \
            [mock.call(LIST_ADDRESS, USER_ADDRESS1, mock.ANY, mock.ANY), \
             mock.call(LIST_ADDRESS, USER_ADDRESS2, mock.ANY, mock.ANY)])
        args = self.db.ping.call_args
        expectedSubject = "Canary Email " + args[0][3]

        # Assert emails were sent
        self.assertEqual(1, self.smtp.sendmail.call_count)
        args = self.smtp.sendmail.call_args[0]
        self.assertEqual(FROM_ADDRESS, args[0])
        self.assertEqual(LIST_ADDRESS, args[1])
        msg = email.message_from_string(args[2])
        self.assertEqual(FROM_ADDRESS, msg['From'])
        self.assertEqual(LIST_ADDRESS, msg['To'])
        self.assertEqual(expectedSubject, msg['Subject'])

    def testCheck(self):
        # Setup mocks
        expectedUUID = "1234-5678-9012-3456"
        self.db.get_accounts.return_value = [ \
            (LIST_ADDRESS, USER_ADDRESS1, SERVER, PASSWORD), \
            (LIST_ADDRESS, USER_ADDRESS2, SERVER, PASSWORD)]
        canary.emailutils.get_mail_uids.return_value = [1]
        canary.emailutils.get_message.return_value = {'Subject': "Canary Email " + expectedUUID}

        # Test check
        self.canary.check(LIST_ADDRESS)

        # Assert DB calls
        self.db.get_accounts.assert_called_with(LIST_ADDRESS)
        self.db.pong.assert_has_calls([ \
            mock.call(USER_ADDRESS1, mock.ANY, expectedUUID), \
            mock.call(USER_ADDRESS2, mock.ANY, expectedUUID)])

        # Assert mail calls
        canary.emailutils.get_imap.assert_has_calls([ \
            mock.call(SERVER, USER_ADDRESS1, PASSWORD), \
            mock.call(SERVER, USER_ADDRESS2, PASSWORD)])
        canary.emailutils.get_message.assert_called_with(canary.emailutils.get_imap.return_value, 1)
        canary.emailutils.delete_message.assert_called_with(canary.emailutils.get_imap.return_value, 1)
        canary.emailutils.close.assert_called_with(canary.emailutils.get_imap.return_value)

    def testDontDeleteOtherMail(self):
        # Setup mocks
        self.db.get_accounts.return_value = [(LIST_ADDRESS, USER_ADDRESS1, SERVER, PASSWORD)]
        canary.emailutils.get_mail_uids.return_value = [1]
        canary.emailutils.get_message.return_value = {'Subject': "Buy Our New Widget"}

        # Test check
        self.canary.check(LIST_ADDRESS)

        # Assert DB calls
        self.db.get_accounts.assert_called_with(LIST_ADDRESS)
        self.db.pong.assert_not_called()

        # Assert mail calls
        canary.emailutils.get_imap.assert_called_with(SERVER, USER_ADDRESS1, PASSWORD)
        canary.emailutils.get_message.assert_called_with(canary.emailutils.get_imap.return_value, 1)
        canary.emailutils.delete_message.assert_not_called()
        canary.emailutils.close.assert_called_with(canary.emailutils.get_imap.return_value)


