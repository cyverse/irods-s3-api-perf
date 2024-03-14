# -*- coding: utf-8 -*-

"""This is the implementation of a Tool class for iCommands.

This tool requires that iCommands version 4.3+ is installed. It also requires
that an iCommands session be initialized for the iRODS zone where performance
testing will happen.
"""

import subprocess

from suite import TestFailure, Tool


class ICommands(Tool):
    """This provides the transfer logic for testing iCommands."""

    def name(self):
        return 'iCommands'

    def download(self, path):
        subprocess.run(['iget', path], check=False)

    def upload(self, path):
        results = subprocess.run(['iput', path], capture_output=True, check=False)
        if results.returncode != 0:
            raise TestFailure(results.stderr.decode())
