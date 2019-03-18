#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import controller
import model
import view
import unittest
from unittest import mock


class TestAppController(unittest.TestCase):

    def setUp(self):
        model.AppModel = mock.Mock()
        view.AppView = mock.MagicMock()
        self.c = controller.AppController("App", "0.0", "path", "1.1.1")
        self.c.model = model.AppModel("App", "path", "1.1.1")
        self.c.view = view.AppView()

    def test_create_gui(self):
        lines = ["# 127.0.0.1  www.python.org  python.org  ",
                 "#127.0.0.1www.pylonsproject.org pylonsproject.org",
                 "127.0.0.1 flask.pocoo.org www.flask.pocoo.org"]
        sites = [(False, "python.org", "www.python.org"),
                 (True, "flask.pocoo.org", "www.flask.pocoo.org")]
        self.c.model.read_file = mock.Mock(return_value=lines)
        self.c.model.extract_sites = mock.Mock(return_value=sites)
        self.c.create_gui()
        self.c.model.read_file.assert_called_once()
        self.c.model.extract_sites.assert_called_once_with(lines)
        self.c.view.load_from_file.assert_called_once_with(sites)
        self.c.view.register.assert_called_once()
        self.c.view.root.title.assert_called_once_with("App 0.0")
        self.c.view.mainloop.assert_called_once()

    def test_add_user_input_0(self):
        """user_inp:
        - zawiera dozwolone znaki - validate_data zwraca True
        - nie istnieje na liście stron (all_sites)
        - zostaje więc dodany
        """
        user_inp = "linuxmint.com"
        all_sites = [("flask.pocoo.org", "www.flask.pocoo.org"),
                     ("java.com", "www.java.com"),
                     ("python.org", "www.python.org")]
        validate = True
        compl_user_inp = ("linuxmint.com", "www.linuxmint.com")
        # self.c.view.get_user_input = mock.Mock(return_value=user_inp)
        # self.c.view.get_all_sites = mock.Mock(return_value=all_sites)
        pm_user_inp = mock.PropertyMock(return_value=user_inp)
        pm_all_sites = mock.PropertyMock(return_value=all_sites)
        type(self.c.view).user_input = pm_user_inp
        type(self.c.view).all_sites = pm_all_sites
        # skąd to type()?
        # > Because of the way mock attributes are stored you can’t directly
        # > attach a PropertyMock to a mock object. Instead you can attach it to
        # > the mock type object
        # zob. https://docs.python.org/3.6/library/unittest.mock.html#unittest.mock.PropertyMock
        # zob. https://kristofclaes.github.io/2016/06/24/mocking-properties-in-python/
        self.c.model.validate_data = mock.Mock(return_value=validate)
        self.c.model.complete_user_input = mock.Mock(return_value=compl_user_inp)
        self.c.add_user_input()
        pm_user_inp.assert_called_once_with()
        pm_all_sites.assert_called_once_with()
        # skąd to assert_called_once_with()?
        # zob. https://docs.python.org/3.6/library/unittest.mock.html#unittest.mock.PropertyMock
        self.c.model.validate_data.assert_called_once_with(user_inp)
        self.assertTrue(self.c.model.validate_data())
        self.c.view.showerr.assert_not_called()
        self.c.model.complete_user_input.assert_called_once_with(user_inp)
        self.c.view.showerr.assert_not_called()
        self.c.view.add_to_listbox.assert_called_once_with(True, compl_user_inp)

    def test_add_user_input_1(self):
        """user_inp:
        - zawiera dozwolone znaki - `validate_data` zwraca True
        - ale istnieje już na liście stron (all_sites) - `add_user_input` zwraca
          False
        - wywołana zostaje funkcja showerr
        - user_inp nie zostaje więc dodany
        """
        user_inp = "www.python.org"
        all_sites = [("flask.pocoo.org", "www.flask.pocoo.org"),
                     ("java.com", "www.java.com"),
                     ("python.org", "www.python.org")]
        validate = True
        compl_user_inp = ("python.org", "www.python.org")
        pm_user_inp = mock.PropertyMock(return_value=user_inp)
        pm_all_sites = mock.PropertyMock(return_value=all_sites)
        type(self.c.view).user_input = pm_user_inp
        type(self.c.view).all_sites = pm_all_sites
        self.c.model.validate_data = mock.Mock(return_value=validate)
        self.c.model.complete_user_input = mock.Mock(return_value=compl_user_inp)
        result = self.c.add_user_input()
        pm_user_inp.assert_called_once_with()
        pm_all_sites.assert_called_once_with()
        self.c.model.validate_data.assert_called_once_with(user_inp)
        self.assertTrue(self.c.model.validate_data())
        self.c.model.complete_user_input.assert_called_once_with(user_inp)
        self.c.view.showerr.assert_called_once_with(self.c.errmsg['exists'])
        self.assertFalse(result)
        self.c.view.add_to_listbox.assert_not_called()

    def test_add_user_input_2(self):
        """user_inp:
        - zawiera niedozwolone znaki - `validate_data` zwraca False
        - więc cała funckja zwraca False
        - wywołana zostaje funkcja showerr
        - user_inp nie zostaje dodany
        """
        user_inp = "?linuxmint.com"
        all_sites = [("flask.pocoo.org", "www.flask.pocoo.org"),
                     ("java.com", "www.java.com"),
                     ("python.org", "www.python.org")]
        validate = False
        # compl_user_inp = ("linuxmint.com", "www.linuxmint.com")
        pm_user_inp = mock.PropertyMock(return_value=user_inp)
        pm_all_sites = mock.PropertyMock(return_value=all_sites)
        type(self.c.view).user_input = pm_user_inp
        type(self.c.view).all_sites = pm_all_sites
        self.c.model.validate_data = mock.Mock(return_value=validate)
        self.c.model.complete_user_input = mock.Mock()
        result = self.c.add_user_input()
        pm_user_inp.assert_called_once_with()
        pm_all_sites.assert_called_once_with()
        self.c.model.validate_data.assert_called_once_with(user_inp)
        self.c.view.showerr.assert_called_once_with(self.c.errmsg['invalid'])
        self.assertFalse(result)
        self.c.model.complete_user_input.assert_not_called()
        self.c.view.add_to_listbox.assert_not_called()


if __name__ == '__main__':
    unittest.main()
