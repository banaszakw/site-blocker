#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import controller
import os
import subprocess

APP_NAME = "SiteBlocker"
VERSION = "1.0"
FPATH = "/etc/hosts"
HOST = "127.0.0.1"


def main():
    isroot = subprocess.check_output('whoami').strip() == b'root'
    if isroot:
        c = controller.AppController(APP_NAME, VERSION, FPATH, HOST)
        c.create_gui()
    else:
        print("Uruchamiasz", APP_NAME, "v.", VERSION)
        subprocess.call(['sudo', '-S', 'python3', os.path.realpath(__file__)])
        # subprocess.run(['gksudo', '--sudo-mode', 'python3', __file__])
        # subprocess.call(['pkexec', 'python3', os.path.realpath(__file__)])


if __name__ == "__main__":
    # execute only if run as a script
    main()
