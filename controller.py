#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import model
import view
from typing import Dict, List, Tuple

ERRMSG: Dict[str, str] = {'invalid': "Wprowadzone dane zawierają niedozwolone "
                                     "znaki lub nic nie wprowadzono",
                          'exists': "Strona już istnieje na liście"}
# 'invalid':"Input contains the invalid characters or input is empty"
# 'exists': "Site already exists on the list"


class AppController:
    """ Class doc """

    def __init__(self, app_name: str, version: str, fpath: str, host: str):
        """ Class initialiser """
        self.app_name = app_name
        self.version = version
        self.fpath = fpath
        self.host = host
        self.model = model.AppModel(self.app_name, self.fpath, self.host)
        self.view = None
        self.errmsg = ERRMSG

    def create_gui(self):
        """Creates application GUI."""
        self.view = view.AppView()
        lines: List[str] = self.model.read_file()
        sites: List[Tuple[bool, str, str]] = self.model.extract_sites(lines)
        self.view.load_from_file(sites)
        self.view.register(self)
        self.view.root.title(" ".join((self.app_name, self.version)))
        self.view.mainloop()

    def add_user_input(self):  # OK
        """Pobiera adres strony podany przez użytkownika, sprawdza jego
        poprawność, to czy jest unikatowy i dodaje go lub zwraca błąd."""
        user_inp: str = self.view.user_input
        all_sites: List[Tuple[str, str]] = self.view.all_sites
        if not self.model.validate_data(user_inp):
            self.view.showerr(self.errmsg['invalid'])
            return False
        user_inp: Tuple[str, str] = self.model.complete_user_input(user_inp)
        if user_inp in all_sites:
            self.view.showerr(self.errmsg['exists'])
            return False
        self.view.add_to_listbox(True, user_inp)

    def block_selected(self):
        self.model.write_file(self.view.all_sites, self.view.sel_sites)


def main():
    AppController("Aplikacja", "0.0", "", "")


if __name__ == "__main__":
    # execute only if run as a script
    main()
