# -*- coding: utf-8 -*-

"""This is the implementation of a Tool class for GoCommands.

This tool requires that GoCommands version 0.7+ is installed. It also requires
that a GoCommands session be initialized for the iRODS zone where performance
testing will happen.
"""

import subprocess

from suite import Tool


class GoCommands(Tool):
    """This provides the transfer logic for testing GoCommands."""

    def name(self):
        return "GoCommands"

    def download(self, path):
        subprocess.run(['gocmd', 'get', path], check=False)

    def upload(self, path):
        subprocess.run(['gocmd', 'put', path], check=False)
