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

    def __str__(self):
        return 'iCommands'

    def download(self, path: str):
        results = subprocess.run(['iget', path], capture_output=True,
                                 check=False)
        if results.returncode != 0:
            raise TestFailure(results.stderr.decode())

    def upload(self, path: str):
        results = subprocess.run(['iput', path], capture_output=True,
                                 check=False)
        if results.returncode != 0:
            raise TestFailure(results.stderr.decode())
