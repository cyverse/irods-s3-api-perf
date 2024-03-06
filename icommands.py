# -*- coding: utf-8 -*-

"""TODO document"""

import subprocess

from suite import TestFailure, Tool


class ICommands(Tool):
    """TODO document"""

    def name(self):
        return 'iCommands'

    def download(self, path):
        subprocess.run(['iget', path], check=False)

    def upload(self, path):
        results = subprocess.run(['iput', path], capture_output=True, check=False)
        if results.returncode != 0:
            raise TestFailure(results.stderr.decode())
