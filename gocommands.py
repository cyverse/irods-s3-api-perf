# -*- coding: utf-8 -*-

"""TODO document"""

import subprocess

from suite import Tool


class GoCommands(Tool):
    """TODO document"""

    def name(self):
        return "GoCommands"

    def download(self, path):
        subprocess.run(['gocmd', 'get', path], check=False)

    def upload(self, path):
        subprocess.run(['gocmd', 'put', path], check=False)
