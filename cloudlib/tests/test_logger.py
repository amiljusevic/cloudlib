# Copyright 2015, Kevin Carter.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import mock

from cloudlib import logger


class Stat(object):
    def __init__(self, uid, gid):
        self.st_uid = uid
        self.st_gid = gid
        self.st_size = 0
        self.st_mtime = 0
        self.st_mode = 0


class TestLogger(unittest.TestCase):
    def setUp(self):
        self.log = logger.LogSetup()

        self.uid_patched = mock.patch('cloudlib.logger.os.getuid')
        self.uid = self.uid_patched.start()

        self.env_patched = mock.patch('cloudlib.logger.os.path.expanduser')
        self.env = self.env_patched.start()

        self.idr_patched = mock.patch('cloudlib.logger.os.path.isdir')
        self.idr = self.idr_patched.start()

        self.stat_patched = mock.patch('cloudlib.logger.os.stat')
        self.stat = self.stat_patched.start()

    def tearDown(self):
        self.uid_patched.stop()
        self.env_patched.stop()
        self.idr_patched.stop()

    def test_logger_max_backup(self):
        self.assertEqual(self.log.max_backup, 5)

    def test_logger_max_size(self):
        self.assertEqual(self.log.max_size, 524288000)

    def test_logger_debug_logging(self):
        self.assertEqual(self.log.debug_logging, False)

    def test_logger_override_backup(self):
        log = logger.LogSetup(max_backup=10)
        self.assertEqual(log.max_backup, 10)

    def test_logger_override_max_backup(self):
        log = logger.LogSetup(max_backup=10)
        self.assertEqual(log.max_backup, 10)

    def test_logger_override_max_size(self):
        log = logger.LogSetup(max_size=10)
        self.assertEqual(log.max_size, 10485760)

    def test_logger_debug_logging_enabled(self):
        log = logger.LogSetup(debug_logging=True)
        self.assertEqual(log.debug_logging, True)

    def test_logger_return_logfile_not_root_new_log_dir(self):
        self.uid.return_value = 99
        self.env.return_value = '/home/TestUser'
        self.idr.return_value = False
        self.stat.return_value = Stat(uid=99, gid=99)
        logfile = self.log.return_logfile(
            filename='test_file', log_dir='/other'
        )
        self.assertEqual(logfile, '/home/TestUser/test_file')

    def test_logger_return_logfile_root_new_log_dir(self):
        self.uid.return_value = 0
        self.env.return_value = '/root'
        self.idr.return_value = True
        self.stat.return_value = Stat(uid=0, gid=0)
        logfile = self.log.return_logfile(
            filename='test_file', log_dir='/other'
        )
        self.assertEqual(logfile, '/other/test_file')

    def test_logger_return_logfile_not_root(self):
        self.uid.return_value = 99
        self.env.return_value = '/home/TestUser'
        self.stat.return_value = Stat(uid=0, gid=0)
        logfile = self.log.return_logfile(filename='test_file')
        self.assertEqual(logfile, '/home/TestUser/test_file')

    def test_logger_return_logfile_root(self):
        self.uid.return_value = 0
        self.env.return_value = '/root'
        self.idr.return_value = True
        self.stat.return_value = Stat(uid=0, gid=0)
        logfile = self.log.return_logfile(filename='test_file')
        self.assertEqual(logfile, '/var/log/test_file')

    def test_logger_return_logfile_root_log_dir_not_found(self):
        self.uid.return_value = 0
        self.env.return_value = '/root'
        self.idr.return_value = False
        logfile = self.log.return_logfile(
            filename='test_file', log_dir='/other'
        )
        self.assertEqual(logfile, '/root/test_file')


class TestLoggerHandlers(unittest.TestCase):
    def setUp(self):

        self.rh_patched = mock.patch(
            'cloudlib.logger.handlers.RotatingFileHandler'
        )
        self.rh = self.rh_patched.start()

        self.sh_patched = mock.patch('cloudlib.logger.logging.StreamHandler')
        self.sh = self.sh_patched.start()

        self.ch_patched = mock.patch(
            'cloudlib.logger.logging.Logger.callHandlers'
        )
        self.ch_patched.start()

        self.log = logger.LogSetup()

        self._log = mock.Mock()
        self._handler = mock.Mock()

    def tearDown(self):
        self.rh_patched.stop()
        self.sh_patched.stop()
        self.ch_patched.stop()

    def test_getlogger_new_logger(self):
        log = logger.getLogger(name='testLogger')
        for handler in log.handlers:
            return self.assertTrue(handler.name == 'testLogger')
        else:
            self.fail('The log handler name was not set')

    def test_logger_default_logger(self):
        self.log.default_logger(
            name='test_log', enable_file=False, enable_stream=False
        )
        format = '%(asctime)s - %(module)s:%(levelname)s => %(message)s'
        self.assertEqual(self.log.format._fmt, format)

    def test_logger_default_logger_new_formatter(self):
        self.log.format = '%(test)s'
        self.log.default_logger(
            name='test_log', enable_file=False, enable_stream=False
        )
        self.assertEqual(self.log.format, '%(test)s')

    def test_logger_enable_file(self):
        self.log.default_logger(
            name='test_log', enable_file=True, enable_stream=False
        )
        self.assertTrue(self.rh.called)
        self.assertFalse(self.sh.called)

    def test_logger_enable_stream(self):
        self.log.default_logger(
            name='test_log', enable_file=False, enable_stream=True
        )
        self.assertFalse(self.rh.called)
        self.assertTrue(self.sh.called)

    def test_logger_enable_stream_enable_file(self):
        self.log.default_logger(
            name='test_log', enable_file=True, enable_stream=True
        )
        self.assertTrue(self.rh.called)
        self.assertTrue(self.sh.called)

    def test_logger_set_handler(self):
        self.log.set_handler(log=self._log, handler=self._handler)
        self.assertTrue(self._log.setLevel.called)
        self.assertTrue(self._handler.setFormatter.called)
        self.assertTrue(self._log.addHandler.called)
