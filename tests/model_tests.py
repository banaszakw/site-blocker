#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import model
import sys
import unittest
from unittest import mock

HOSTS_FILE = r"""127.0.0.1    localhost
127.0.1.1    nuc

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
# BEGIN SiteBlocker
# 127.0.0.1 python.org www.python.org
 foo 

 
127.0.0.1 java.com www.java.com
# END SiteBlocker

"""

HOSTS_FILE_EMPTY = r"""127.0.0.1    localhost
127.0.1.1    nuc

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

"""

RIGHT_HOSTS = ["# 127.0.0.1 python.org www.python.org",
               "foo",
               "127.0.0.1 java.com www.java.com"]
RIGHT_HOSTS_EMPTY = []
SITES = []


class TestAppModel(unittest.TestCase):

    def setUp(self):
        self.HOSTS_FILE = io.StringIO(HOSTS_FILE)
        self.HOSTS_FILE_EMPTY = io.StringIO(HOSTS_FILE_EMPTY)
        self.model = model.AppModel("SiteBlocker", "", "127.0.0.1")
        # self.model.FPATH = self.HOSTS_FILE

    @unittest.skipIf(sys.version_info < (3, 5), "Tylko dla Py >= 3,5")
    def test_read_file_0(self):  # OK
        with mock.patch('model.open') as mopen:  # Linux
            # mock_open mozna uzyc, gdy testowana funkcja wykorzystuje read(),
            # readline() albo readlines()!
            mopen.return_value = self.HOSTS_FILE
            result = self.model.read_file()
            self.assertListEqual(RIGHT_HOSTS, result)

    @unittest.skipIf(sys.version_info < (3, 5), "Tylko dla Py >= 3,5")
    def test_read_file_1(self):  # OK
        with mock.patch('model.open') as mopen:  # Linux
            # mock_open mozna uzyc, gdy testowana funkcja wykorzystuje read(),
            # readline() albo readlines()!
            mopen.return_value = self.HOSTS_FILE_EMPTY
            result = self.model.read_file()
            self.assertListEqual(RIGHT_HOSTS_EMPTY, result)

    @unittest.skipIf(sys.version_info >= (3, 5), "Tylko dla Py < 3,5")
    @unittest.skip("Cały program wymaga Pythona >= 3,6, więc można pominąć "
                   "testowanie dostsowane do Py < 3,5")
    def test_read_file_2(self):  # OK
        with mock.patch('builtins.open') as mopen:  # Win + Py 3.4
            # mock_open mozna uzyc, gdy testowana funkcja wykorzystuje read(),
            # readline() albo readlines()!
            mopen.return_value = self.HOSTS_FILE
            result = self.model.read_file()
            self.assertListEqual(RIGHT_HOSTS, result)

    def test_extract_sites_0(self):
        lines = ["# 127.0.0.1  www.python.org  python.org  ",
                 "#127.0.0.1www.pylonsproject.org pylonsproject.org",
                 "127.0.0.1 flask.pocoo.org www.flask.pocoo.org"]
        out_sites = [(False, "python.org", "www.python.org"),
                     (True, "flask.pocoo.org", "www.flask.pocoo.org")]
        result = self.model.extract_sites(lines)
        self.assertListEqual(out_sites, result)

    def test_extract_sites_1(self):
        lines = []
        out_sites = []
        result = self.model.extract_sites(lines)
        self.assertListEqual(out_sites, result)

    def test_extract_data(self):
        testsmap = {
            "# 127.0.0.1  www.python.org  python.org  ":
                (False, "python.org", "www.python.org"),
            "127.0.0.1 java.com www.java.com":
                (True, "java.com", "www.java.com"),
            " # 127.0.0.1  www.perl.org perl.org":
                (False, "perl.org", "www.perl.org"),
            "#127.0.0.1  www.scala-lang.org scala-lang.org":
                (False, "scala-lang.org", "www.scala-lang.org"),
            "#127.0.0.1  www.rust-lang.org rust-lang.org":
                (False, "rust-lang.org", "www.rust-lang.org"),
            "   127.0.1.1 flask.pocoo.org www.flask.pocoo.org":
                (True, "flask.pocoo.org", "www.flask.pocoo.org"),
            " #127.0.0.1  www.linuxmint.com": (False, "", "www.linuxmint.com"),
            "   127.0.0.1  xubuntu.com": (True, "xubuntu.com", ""),
            "#127.0.0.1www.pylonsproject.org pylonsproject.org": None,
            "": None}
        for line, alist in testsmap.items():
            with self.subTest():
                result = self.model.extract_data(line)
                self.assertEqual(alist, result)

    @unittest.skip("Niepotrzebne")
    def test_extract_sites_map(self):
        lines = ["# 127.0.0.1  www.python.org  python.org  ",
                 "#127.0.0.1www.pylonsproject.org pylonsproject.org",
                 "127.0.0.1 flask.pocoo.org www.flask.pocoo.org"]
        out_sites = [
            (False, "python.org", "www.python.org"),
            None,
            (True, "flask.pocoo.org", "www.flask.pocoo.org")]
        result = map(self.model.extract_data, lines)
        self.assertListEqual(out_sites, list(result))

    def test_validate_data(self):
        testsmap = {
            "www.test.com ": True,
            "www.test. com": False,
            "www.test.com\n": True,
            "www.test.com/index": False,
            "www.test-test.com": True,
            "www.test_test.com": True,
            "www.test_test,com": False,
            "ww.test.com": True,
            "1test.com": False,
            "-test.com": False,
            "t1est.com": True,
            "_test.com": False,
            "t_est.com": True
        }
        for s, b in testsmap.items():
            with self.subTest():
                result = self.model.validate_data(s)
                self.assertEqual(b, result)

    def test_complete_user_input(self):
        testmap = {'www.foo.com': ('foo.com', 'www.foo.com'),
                   'bar.com': ('bar.com', 'www.bar.com')}
        for inp, complete in testmap.items():
            with self.subTest():
                result = self.model.complete_user_input(inp)
                self.assertTupleEqual(complete, result)

    @unittest.skip("Funkcja będzie usunięta z model.py")
    def test_isunique(self):
        pass

    def test_write_file_0(self):
        mall_sites = [("flask.pocoo.org", "www.flask.pocoo.org"),
                      ("java.com", "www.java.com"),
                      ("python.org", "www.python.org")]
        out = [mock.call().write('# BEGIN SiteBlocker\n'),
               mock.call().write(" ".join("""127.0.0.1 flask.pocoo.org
                                 www.flask.pocoo.org \n""".split()) + ' \n'),
               mock.call().write('# 127.0.0.1 java.com www.java.com \n'),
               mock.call().write('127.0.0.1 python.org www.python.org \n'),
               mock.call().write('# END SiteBlocker\n')]
        self.model.clear_hosts_file = mock.MagicMock()
        msel = (0, 2)
        m = mock.mock_open()
        with mock.patch('model.open', m):
            self.model.write_file(mall_sites, msel)
            m.assert_called_once_with(self.model.fpath, 'a')
            assert m().write.call_count == 5
            m.assert_has_calls(out)
            self.model.clear_hosts_file.assert_called_once()

    def test_write_file_1(self):
        mall_sites = [("flask.pocoo.org", "www.flask.pocoo.org"),
                      ("java.com", "www.java.com"),
                      ("python.org", "www.python.org")]
        self.model.clear_hosts_file = mock.MagicMock()
        msel = (0, 2)
        with mock.patch('model.open') as mopen:
            # mock_open mozna uzyc, gdy testowana funkcja wykorzystuje read(),
            # readline() albo readlines()!
            mopen.return_value = self.HOSTS_FILE
            # result = self.model.read_file()`
            # self.assertListEqual(RIGHT_HOSTS, result)
            self.assertIsNone(self.model.write_file(mall_sites, msel))
            self.model.clear_hosts_file.assert_called_once()

    @unittest.skip("Funkcja nieużywana")
    def test_sort_line(self):
        pass

    def test_clear_hosts_file_0(self):
        # out = r"""127.0.0.1    localhost\n
        #           127.0.1.1    nuc\n\n
        #           # The following lines are desirable for IPv6 capable hosts\n
        #           ::1     ip6-localhost ip6-loopback\n
        #           fe00::0 ip6-localnet\n
        #           ff00::0 ip6-mcastprefix\n
        #           ff02::1 ip6-allnodes\n
        #           ff02::2 ip6-allrouters\n\n"""
        out = HOSTS_FILE_EMPTY
        # out = '\n'.join([l.strip() for l in out.split('\\n')])
        m = mock.mock_open(read_data=HOSTS_FILE)
        with mock.patch('model.open', m):
            self.model.clear_hosts_file()
            m.assert_called_once_with(self.model.fpath, 'r+')
            m().write.assert_called_once_with(out)

    def test_clear_hosts_file_1(self):
        """W pliku hosts nie ma nic do usunięcia - brak znaczników `BEGIN`
        i `END`"""
        out = HOSTS_FILE_EMPTY
        m = mock.mock_open(read_data=HOSTS_FILE_EMPTY)
        with mock.patch('model.open', m):
            self.model.clear_hosts_file()
            m.assert_called_once_with(self.model.fpath, 'r+')
            m().write.assert_called_once_with(out)


def main():

    return 0


if __name__ == "__main__":
    unittest.main()
    # unittest.main(verbosity=2)
