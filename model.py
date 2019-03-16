#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import List, Tuple
import re


class AppModel:
    """ Model """

    def __init__(self, app_name: str, fpath: str, host: str):
        self.app_name = app_name
        self.fpath = fpath
        self.host = host
        self.head = r"# BEGIN {}".format(self.app_name)
        self.foot = r"# END {}".format(self.app_name)

    def read_file(self) -> List[str]:  # OK
        """Czyta wiersz po wierszu plik `hosts`, usuwa białe znaki, pobiera
        z niego wiersze pomiędzy znacznikami `BEGIN` i `END` (nie pobiera
        znaczników). Zwraca listę z wierszami.
        """
        lines = []
        with open(self.fpath, 'r') as fr:
            read = False
            for line in fr:
                line = line.strip()
                if line.startswith(self.head):
                    read = True
                    continue
                elif line.startswith(self.foot):
                    read = False
                if read and line != '':
                    lines.append(line)
        return lines

    def extract_sites(self, lines: List[str]) -> List[Tuple[bool, str, str]]:  # OK
        """ Dla każdego elementu listy wywołuje `extract_data`, która konwertuje
        go na krotkę. Ta funkcja usuwa elementy None."""
        sites: Tuple[bool, str, str] or None = map(self.extract_data, lines)
        return [s for s in sites if s is not None]

    def extract_data(self, s: str) -> Tuple[bool, str, str] or None:  # OK
        """ Pomocnicza funkcja dla `extract_sites`. Z podanej lini pliku hosts
        wyodrębnia `#` (jeśli jest), dwa adresy strony (jeśli nie znajdzie
        ktoregoś, zastąpi je pustym stingiem) i zwraca je jako krotkę.
        s -- wiersz z pliku hosts
        """
        patt = re.compile(r"""(\s*\#*\s*)
                              (\d{3}.\d{1}.\d{1}.\d{1})
                              (\s+)
                              ([\w\.\-]+)
                              (\s*)
                              ([\w\.\-]*)""", re.VERBOSE)
        try:
            m = re.match(patt, s)
            if m.group(1).strip().startswith("#"):
                blocked: bool = False
            else:
                blocked: bool = True
            lin: List[str] = sorted((m.group(4), m.group(6)),
                                    key=lambda i: i.startswith("www."))
            # lin.insert(0, blocked)
            # lin = (blocked,) + tuple(lin)
            return blocked, lin[0], lin[1]
        except AttributeError:
            return None

    def validate_data(self, inp: str) -> bool:  # OK
        """ Sprawdza poprawnośc wprowadzonych danych: 1) czy zaczyna się od
        znaków alfabetycznych 2) czy zawierają dozwolone znaki: alfanumeryczne,
        podkreślnik, kropkę, dywiz, c. Zwraca True lub False.
        inp -- dane wprowadzone przez użytkownika
        """
        inp = inp.strip()
        if re.match(r"[a-zA-Z]", inp):
            if re.search(r"^[\w.-]+$", inp):
                return True
        return False

    def complete_user_input(self, inp: str) -> Tuple[str, str]:  # OK
        """ Sprawdza, czy adres strony rozpoczyna się od `wwww.`. Jeśli nie,
        dodaje go, jeśli tak, usuwa. Zwraca zawsze dwuelementową krotkę:
        (adres.com, www.adres.com).
        """
        patt = r"^www\."
        if re.match(patt, inp):
            return re.sub(patt, '', inp), inp
        else:
            return inp, "www." + inp

    def write_file(self, all_sites: List[Tuple[str, str]],  # OK
                   sel: Tuple[int, ...]) -> None:
        """ Zapisuje dane do pliku hosts. Wcześniej czyści plik hosts między
        znacznikami `BEGIN` i `END`. (włącznie ze znacznikami). """
        self.clear_hosts_file()
        with open(self.fpath, 'a') as fw:
            fw.write(self.head + '\n')
            for n, site in enumerate(all_sites):
                if n in sel:
                    fw.write(" ".join((self.host, *site, '\n')))
                    # Dla Py < 3,5:
                    # fw.write(" ".join((self.host, site[0], site[1], '\n')))
                    # https://stackoverflow.com/a/33973612
                else:
                    fw.write(" ".join(('#', self.host, *site, '\n')))
                    # Dla Py < 3,5:
                    # fw.write(" ".join(('#', self.host, site[0], site[1], '\n')))
                    # https://stackoverflow.com/a/33973612
            fw.write(self.foot + '\n')

    # def sort_line(self, line):
    #     line[1:] = sorted(line[1:])
    #     return line

    def clear_hosts_file(self) -> None:  # OK
        """ Usuwa wiersze pomiędzy znacznikami `BEGIN` i `END` włacznie z samymi
        liniami ze znacznikami.
        """
        with open(self.fpath, 'r+') as fr:
            fr.seek(0)
            rewritten: List[str] = []
            rewrite: bool = True
            # readlines() - niewydajne dla dużych plików, ale hosts jest mały
            for line in fr.readlines():
                if line.startswith(self.head):
                    rewrite = False
                elif line.startswith(self.foot):
                    rewrite = True
                    continue
                if rewrite:
                    rewritten.append(line)
            fr.truncate(0)
            fr.seek(0)
            fr.write(''.join(rewritten))


def main():
    AppModel("Aplikacja", "", "")


if __name__ == "__main__":
    # execute only if run as a script
    main()
