import unittest
import tempfile, shutil
import datetime

from emailcanary import canarydb

class TestCanaryDB(unittest.TestCase):
	def setUp(self):
		self.tempdir = tempfile.mkdtemp()
		self.db = canarydb.CanaryDB(self.tempdir + "canary.db")

	def tearDown(self):
		self.db.close()
		shutil.rmtree(self.tempdir)

	def testPingCheckPong(self):
		address = "test@example.com"
		time = datetime.datetime(2015, 10, 24, 9, 00)
		uuid = "1234"
		expectedDelta = datetime.datetime.now() - time

		# Record a Ping
		self.db.ping(address, time, uuid)

		# Check for missing pongs
		missing = self.db.get_missing_pongs()

		self.assertEqual(1, len(missing))
		firstMissing = missing[0]
		self.assertEqual(3, len(firstMissing))
		self.assertEqual(uuid, firstMissing[0])
		self.assertEqual(address, firstMissing[1])
		delta = firstMissing[2].total_seconds() - expectedDelta.total_seconds()
		self.assertTrue(delta <= 10)

		# Record a pong
		pongtime = datetime.datetime(2015, 10, 24, 9, 05)
		self.db.pong(address, pongtime, uuid)

		# Check for missing pongs
		missing = self.db.get_missing_pongs()
		self.assertEqual(0, len(missing))

	def testCloseReopen(self):
		address = "test@example.com"
		time = datetime.datetime(2015, 10, 24, 9, 00)
		uuid = "1234"
		expectedDelta = datetime.datetime.now() - time

		# Record a Ping
		self.db.ping(address, time, uuid)

		# Close, Reopen
		self.db.close()
		self.db = canarydb.CanaryDB(self.tempdir + "canary.db")

		# Check for missing pongs
		missing = self.db.get_missing_pongs()

		self.assertEqual(1, len(missing))
		firstMissing = missing[0]
		self.assertEqual(3, len(firstMissing))
		self.assertEqual(uuid, firstMissing[0])
		self.assertEqual(address, firstMissing[1])
		delta = firstMissing[2].total_seconds() - expectedDelta.total_seconds()
		self.assertTrue(delta <= 10)

	def testAccounts(self):
		listAddress = "list@example.org"
		address = "user@example.net"
		imapserver = "imap.example.net"
		password = "secretpassword"

		# Verify that no accounts exist
		accounts = self.db.get_accounts()
		self.assertEqual(0, len(accounts))

		# Add one account
		self.db.add_account(listAddress, address, imapserver, password)

		# Verify that the account exists
		accounts = self.db.get_accounts()
		self.assertEqual(1, len(accounts))
		self.assertEqual(listAddress, accounts[0][0])
		self.assertEqual(address, accounts[0][1])
		self.assertEqual(imapserver, accounts[0][2])
		self.assertEqual(password, accounts[0][3])

		# Remove the account
		self.db.remove_account(address)
		accounts = self.db.get_accounts()
		self.assertEqual(0, len(accounts))

	def testGetRecipientsForList(self):
		listAddress1 = "list1@example.org"
		listAddress2 = "list2@example.org"
		imapserver = "imap.example.net"
		password = "secretpassword"
		address1 = "user1@example.net"
		address2 = "user2@example.net"

		# No accounts
		self.assertEqual([], self.db.get_recipients_for_list(listAddress1));
		self.assertEqual([], self.db.get_recipients_for_list(listAddress2));

		# One account
		self.db.add_account(listAddress1, address1, imapserver, password)
		self.assertEqual([address1], self.db.get_recipients_for_list(listAddress1));
		self.assertEqual([], self.db.get_recipients_for_list(listAddress2));

		# Two accounts
		self.db.add_account(listAddress1, address2, imapserver, password)
		self.assertEqual([address1, address2], self.db.get_recipients_for_list(listAddress1));
		self.assertEqual([], self.db.get_recipients_for_list(listAddress2));

		# Two lists
		self.db.add_account(listAddress2, address1, imapserver, password)
		self.assertEqual([address1, address2], self.db.get_recipients_for_list(listAddress1));
		self.assertEqual([address1], self.db.get_recipients_for_list(listAddress2));
