#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import unittest
import view
from unittest import mock


class TestAppController(unittest.TestCase):

    def setUp(self):
        self.v = view.AppView()
        # print(self.v)
        # self.v.create_input_widget = mock.Mock()
        # self.v.create_input_widget.assert_called_once()

    def test_sel_sites(self):
        curselection = (0, 2, 3)
        tk.Listbox.curselection = mock.Mock(return_value=curselection)
        self.assertTupleEqual(curselection, self.v.sel_sites)

    def test_all_sites(self):
        listboxget = ["flask.pocoo.org    www.flask.pocoo.org",
                      "java.com    www.java.com",
                      "python.org    www.python.org"]
        out = [("flask.pocoo.org", "www.flask.pocoo.org"),
               ("java.com", "www.java.com"),
               ("python.org", "www.python.org")]
        tk.Listbox.get = mock.Mock(return_value=listboxget)
        self.assertListEqual(out, self.v.all_sites)

    def test_user_inp(self):
        out = "www.python.org"
        tk.StringVar.get = mock.Mock(return_value=out)
        self.assertEqual(out, self.v.user_input)

    def test_add_to_listbox_0(self):
        """Nazwa strony jest krótsza niż 16 znaków, więc nie trzeba zmieniać
        ustawienia tabulatora. Wprowadzona strona będzie automatycznie
        zaznaczona - sel = True.
        """
        sel = True
        elem = ("java.com", "www.java.com")
        out = "java.com        www.java.com"
        self.v.listbox = mock.Mock()
        self.v.entry = mock.Mock()
        self.v.add_to_listbox(sel, elem)
        self.v.listbox.insert.assert_called_once_with('end', out)
        self.v.listbox.selection_set.assert_called_once_with(tk.END)
        self.v.entry.delete.assert_called_once_with(0, 'end')
        self.v.entry.focus.assert_called_once()

    def test_add_to_listbox_1(self):
        """Nazwa strony jest krótsza niż 16 znaków, więc nie trzeba zmieniać
        ustawienia tabulatora. Wprowadzona strona nie będzie zaznaczona -
        sel = False.
        """
        sel = False
        elem = ("java.com", "www.java.com")
        out = "java.com        www.java.com"
        self.v.listbox = mock.Mock()
        self.v.entry = mock.Mock()
        self.v.add_to_listbox(sel, elem)
        self.v.listbox.insert.assert_called_once_with('end', out)
        self.v.listbox.selection_set.assert_not_called()
        self.v.entry.delete.assert_called_once_with(0, 'end')
        self.v.entry.focus.assert_called_once()

    def test_add_to_listbox_2(self):
        """Nazwa strony jest dłuższa niż 16 znaków, więc trzeba zmieniać
        ustawienia tabulatora. Wprowadzona strona będzie automatycznie
        zaznaczona - sel = True.
        """
        sel = True
        elem = ("stackoverflow.com", "www.stackoverflow.com")
        out = "stackoverflow.com   www.stackoverflow.com"
        self.v.listbox = mock.Mock()
        self.v.entry = mock.Mock()
        self.v.add_to_listbox(sel, elem)
        self.v.listbox.insert.assert_called_once_with('end', out)
        self.v.listbox.selection_set.assert_called_once_with(tk.END)
        self.v.entry.delete.assert_called_once_with(0, 'end')
        self.v.entry.focus.assert_called_once()

    def test_add_to_listbox_3(self):
        """Nazwa strony jest dłuższa niż 16 znaków, więc trzeba zmieniać
        ustawienia tabulatora. Wprowadzona strona nie będzie zaznaczona -
        sel = False.
        """
        sel = True
        elem = ("stackoverflow.com", "www.stackoverflow.com")
        out = "stackoverflow.com   www.stackoverflow.com"
        self.v.listbox = mock.Mock()
        self.v.entry = mock.Mock()
        self.v.add_to_listbox(sel, elem)
        self.v.listbox.insert.assert_called_once_with('end', out)
        self.v.listbox.selection_set.assert_called_once_with(tk.END)
        self.v.entry.delete.assert_called_once_with(0, 'end')
        self.v.entry.focus.assert_called_once()

    def test_delete_from_listbox_0(self):
        result_map = [((1, 3, 7), [mock.call(7), mock.call(3), mock.call(1)]),
                      ((2,), [mock.call(2)]),
                      ((0, 1, 2, 3), [mock.call(3), mock.call(2), mock.call(1),
                                      mock.call(0)])]
        for cursel, calls in result_map:
            with self.subTest():
                self.v.listbox.curselection = mock.Mock(return_value=cursel)
                self.v.listbox.delete = mock.Mock()
                self.v.delete_from_listbox()
                self.v.listbox.delete.assert_has_calls(calls)

    def test_delete_from_listbox_1(self):
        """Nie zaznaczono nic do usunięcia, ale kliknięto przycisk usunięcia."""
        self.v.listbox.curselection = mock.Mock(return_value=())
        self.v.listbox.delete = mock.Mock()
        self.v.showerr = mock.Mock()
        self.v.delete_from_listbox()
        self.v.listbox.delete.assert_not_called()
        self.v.showerr.assert_called_once_with(self.v.errmsg['notselected'])

    def test_load_user_list_0(self):
        user_list = [(False, "news.google.com", "www.news.google.com"),
                     (True, "stackoverflow.com", "www.stackoverflow.com"),
                     (False, "youtube.com", "www.youtube.com"),
                     (True, "spotify.com", "www.spotify.com")]
        add_calls = [mock.call(False, ("news.google.com", "www.news.google.com")),
                     mock.call(True, ("spotify.com", "www.spotify.com")),
                     mock.call(True, ("stackoverflow.com", "www.stackoverflow.com")),
                     mock.call(False, ("youtube.com", "www.youtube.com"))]
        # select_calls = [mock.call(1), mock.call(2)]  # to indeksy listy posortowanej
        self.v.add_to_listbox = mock.Mock()
        self.v.listbox.selection_set = mock.Mock()    
        self.v.load_from_file(user_list)
        self.v.add_to_listbox.assert_has_calls(add_calls)
        self.assertTrue(self.v.add_to_listbox.call_count == 4)
        self.v.listbox.selection_set.assert_not_called()

    def test_load_user_list_1(self):
        user_list = []
        self.v.add_to_listbox = mock.Mock()
        # self.v.listbox.selection_set = mock.Mock()
        self.v.load_from_file(user_list)
        self.v.add_to_listbox.assert_not_called()
        # self.v.listbox.selection_set.assert_not_called()


def main():
    return 0


if __name__ == "__main__":
    unittest.main()
