from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase
import sys  # to write the output while running unit tests


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """Test waiting for db when db is not available"""
        # override the behavior of the ConnectionHandler
        # use patch to mock the ConnectionHandler
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # the __getitem__ is actually called when you retrieve the database
            # mock the __getitem__ using patch and assign as a variable 'gi'
            # during the test the mock item will override django behavior and
            # replace with mock object which will return value 'True' and allow
            # to monitor how many times the command was called
            gi.return_value = True
            call_command('wait_for_db')  # testing the command 'wait_for_db'

            self.assertEqual(gi.call_count, 1)  # testing the command is called
            # once
            sys.stderr.write(repr('test 1 is done') + '\n')

    @patch('time.sleep', return_value=True)  # in the test it won't wait the
    # seconds, rather speed up the test by replacing the behavior of time.sleep
    # this code does the same as line 14, and it would pass in as an argument
    # to test_wait_for_db function, that is why we use 'ts' even though we are
    # not using it in the test
    def test_wait_for_db(self, ts):
        """test waiting for db"""
        # the number is 6 is used to make it reseasonable in realtime execution
        # any number higher than 1 can be used here
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # 5 times raise the operational error, and the 6th time doesn't
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')

            self.assertEqual(gi.call_count, 6)
            sys.stderr.write(repr('test 2 is done') + '\n')
