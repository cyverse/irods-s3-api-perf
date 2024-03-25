# -*- coding: utf-8 -*-

"""This is the implementation of a Tool class for GoCommands.

This tool requires that GoCommands version 0.7+ is installed. It also requires
that a GoCommands session be initialized for the iRODS zone where performance
testing will happen.
"""

import subprocess

from suite import TestFailure, Tool


class GoCommands(Tool):
    """This provides the transfer logic for testing GoCommands."""

    def __str__(self):
        return "GoCommands"

    def download(self, path: str):
        results = subprocess.run(['gocmd', 'get', path], capture_output=True,
                                 check=False)
        if results.returncode != 0:
            raise TestFailure(results.stderr.decode())

    def upload(self, path: str):
        results = subprocess.run(['gocmd', 'put', path], capture_output=True,
                                 check=False)
        if results.returncode != 0:
            raise TestFailure(results.stderr.decode())
