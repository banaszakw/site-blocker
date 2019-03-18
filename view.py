#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, font, messagebox
from typing import Dict, List, Tuple

ERRMSG: Dict[str, str] = {'notselected': "Nie wybrano żadnej pozycji",
                          'unittests': "View is currently running standalone "
                                       "- for unittests purpose only."}
LABELS: Dict[str, str] = {'add': "Dodaj",
                          'block': "Blokuj",
                          'cancel': "Anuluj",
                          'delete': "Usuń",
                          'err': "Błąd",
                          'insert': "Podaj adres strony:",
                          'select': "Zaznacz strony do zablokowania:"}


class AppView:

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.controller = None
        self.btn_sty = {'pady': (5, 5), 'padx': (5, 5), 'side': tk.RIGHT}
        self.labels: Dict[str, str] = LABELS
        self.errmsg: Dict[str, str] = ERRMSG
        self.create_input_widget()
        self.create_listbox()
        # self.create_dropdown()
        self.root.resizable(True, False)
        self.create_bottom_button_bar()

    def register(self, controller):
        self.controller = controller

    def mainloop(self):
        self.root.mainloop()

    @property
    def sel_sites(self) -> Tuple[int, ...]:
        """Pobiera krotkę z indeksami zaznaczonych pozycji na liście w widżecie
        Listbox.
        """
        return self.listbox.curselection()
    
    @property
    def all_sites(self) -> List[Tuple[str, str]]:
        """Pobiera zawartość listy z widżetu Listbox. Dzieli każdy element listy
        na podstawie spacji i zwraca krotkę.
        """
        return [tuple(site.split()) for site in self.listbox.get('0', tk.END)]

    @property
    def user_input(self) -> str:
        """Pobiera tekst wprowadzony przez użytkownika."""
        return self.site.get()

    def create_input_widget(self):
        self.site = tk.StringVar()
        frame = ttk.Frame(self.root, padding=5)
        ttk.Label(frame, text=self.labels['insert']).pack(fill=tk.X, side=tk.TOP)
        ttk.Button(frame, command=self.add_by_user,
                   text=self.labels['add']).pack(self.btn_sty)
        self.entry = ttk.Entry(frame, text=self.site)
        self.entry.pack(self.btn_sty, expand=1, fill=tk.X)
        self.entry.bind('<Return>', self.add_by_user)
        self.entry.focus()
        frame.pack(expand=0, fill=tk.X)

    def add_to_listbox(self, sel: bool, elem: Tuple[str, str]) -> None:
        """Dodaje listę z parą adresów (xxx.com i www.xxx.com) wprowadzoną przez
        użytkownika do widżetu Listbox i zaznacza wprowadzona pozycję jako
        aktywną. Sprawdza, czy pierwszy element listy jest dłuższy niż 16 znków,
        jeśli tak to przesuwa tabulator o 4 i tak do skutku.
        """
        tab: int = 16
        sitename: int = len(elem[0])
        while sitename >= tab:
            tab += 4
        space: str = ' ' * (tab - len(elem[0]))
        self.listbox.insert(tk.END, space.join(elem))
        if sel:
            self.listbox.selection_set(tk.END)
        self.entry.delete(0, 'end')
        self.entry.focus()

    def delete_from_listbox(self) -> None:
        """Usuwa zaznaczone elementy z widżetu Listbox. Najpierw pobiera krotkę
        z indeksami zaznaczonych elementów, odwraca kolejność w krotce i kasuje
        elementy od tyłu, aby indeksy się nie zmieniły.
        """
        elem: Tuple[int] = self.listbox.curselection()
        if elem:
            for i in reversed(elem):
                self.listbox.delete(i)
        else:
            self.showerr(self.errmsg['notselected'])

    def create_listbox(self):
        frame = ttk.Frame(self.root, padding=5)
        listbox_font = tk.font.Font(family='Monospace', size=10)
        ttk.Label(frame, text=self.labels['select']).pack(fill=tk.X)
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(frame, font=listbox_font,
                                  selectmode=tk.MULTIPLE)
        self.listbox.pack(expand=1, fill=tk.BOTH, side=tk.TOP)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        frame.pack(expand=1, fill=tk.BOTH, side=tk.TOP)

    def add_by_user(self, event=None):
        """Funkcja wywoływana przez naciśnięcie klawisza `Dodaj` lub `Enter`
        przy polu wpisywania strony."""
        try:
            self.controller.add_user_input()
        except AttributeError:
            print(self.errmsg['unittests'])

    def showerr(self, msg):
        messagebox.showerror(title=self.labels['err'], message=msg)
        return 'break'

    def load_from_file(self, sites: List[Tuple[bool, str, str]]):
        """Ładuje zawrtość listy do widżetu Listbox. W tym celu najpierw sortuje
        liste alfabetycznie wg adresu strony bez `www.`, dodaje do widżetu
        Listbox tylko adresy (alist[1:3]), a na podstawie wartosci bool
        (alist[0]) ustawia, czy pozycja w widżecie ma być zaznaczona.
        sites -- lista z parą adresów i informacją czy strona jest zablokowana
        """
        sites: List[Tuple[bool, str, str]] = sorted(sites, key=lambda t: t[1])
        for ind, line in enumerate(sites):
            self.add_to_listbox(line[0], line[1:3])
            # self.add_to_listbox(line[1:3])
            # if line[0]:
            #     self.listbox.selection_set(ind)

    def create_bottom_button_bar(self):
        func = (self.block_selected, self.quit, self.delete_from_listbox)
        labels = ('block', 'cancel', 'delete')
        for fn, lb in zip(func, labels):
            ttk.Button(self.root,
                       command=fn,
                       text=self.labels[lb]).pack(self.btn_sty)

    def block_selected(self):
        try:
            self.controller.block_selected()
        except AttributeError:
            print(self.errmsg['unittests'])

    def quit(self):
        self.root.quit()
        self.root.destroy()


def main():
    view = AppView()
    view.mainloop()


if __name__ == "__main__":
    # execute only if run as a script
    main()
