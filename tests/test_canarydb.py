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
