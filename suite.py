# -*- coding: utf-8 -*-

"""This provides a framework for comparing transfer performance.

Given a set of tools and a set of transfer actions, this module provides a
framework for comparing how long it takes each tool to perform each of the
actions. To estimate how long a tool take to perform an action, the module has a
tool perform an action multiple times. It then reports the geometric mean and
one-geometric standard deviation from the times it took the tool to perform the
action.

A PerformanceSuite object is responsible for doing the performance comparison.
It requires a set of Tool objects, one for each tool under test, a set of
TestFactory objects, one for each action being performed, and a Recorder object,
where results are sent. The PerformanceSuite uses these TestFactory objects to
create Test objects. A Test measures the time it takes a single Tool to perform
a certain action once.
"""

from abc import ABC, abstractmethod
import math
import timeit
from typing import List, Optional

import numpy


class Recorder(ABC):
    """This class delivers messages to the caller."""

    @abstractmethod
    def notify(self, msg:str) -> None:
        """This method sends a notification message.
        Args:
            msg  the message
        """

    @abstractmethod
    def log(self, result:str) -> None:
        """This methods sends a test result to be logged.
        Args:
            result  the test result
        """


class TestFailure(Exception):
    """This indicates that a test has failed.
    Parameters:
        reason  a message providing information about the failure
    """

    def __init__(self, reason:str=""):
        self._reason = reason

    def __str__(self):
        return f"TestFailure: {self._reason}"


class Tool(ABC):
    """This is a tool whose performance is to be tested."""

    @abstractmethod
    def name(self) -> str:
        """This returns the name of the tool."""

    @abstractmethod
    def download(self, path:str) -> None:
        """This downloads a copy of an iRODS data object.
        Args:
            path  This is the path to the data object relative to the current
                working collection. It is also the path to the downloaded file
                relative to the current working directory.
        """

    @abstractmethod
    def upload(self, path:str) -> None:
        """This uploads a file to iRODS.
        Args:
            path  This is the path to the file relative to the current working
                directory. It is also the path to the resulting data object
                relative to the current working collection.
        """


class Test(ABC):
    """This is a performance test.
    A performance test records how long it takes to perform the action being
    tested.
    """

    def __init__(self):
        self.__dt = None

    @abstractmethod
    def _run(self) -> None:
        """This executes the action being tested."""

    @abstractmethod
    def _set_up(self) -> None:
        """This prepares the environment for the run."""

    @abstractmethod
    def _tear_down(self) -> None:
        """This cleans up the environment after the run."""

    def perform(self) -> None:
        """This performs the test."""
        try:
            self._set_up()
            self.__dt = timeit.timeit(self._run, number=1)
        finally:
            try:
                self._tear_down()
            except TestFailure:
                pass

    def duration(self) -> Optional[float]:
        """This returns how long the test took to run in seconds.
        If the test has not been run, `None` is returned.
        """
        return self.__dt


class TestFactory(ABC):
    """This is responsible for creating tests of a specific action."""

    @abstractmethod
    def test_name(self) -> str:
        """This is the name of the test created by this factory."""

    @abstractmethod
    def make_test(self, tool: Tool) -> Test:
        """
        This creates a test that uses a given tool to perform the action being
        tested.

        Args:
            tool  The tool used to perform the action.
        """


class _TestResult:

    def __init__(self, measurements: List[float]):
        if measurements:
            geo_mean = numpy.exp(numpy.log(measurements).mean())
            ln_var = numpy.square(numpy.log(numpy.divide(measurements, geo_mean))).mean()
            self.__geo_mean = geo_mean
            self.__geo_std = numpy.exp(numpy.sqrt(ln_var))
        else:
            self.__geo_mean = float('nan')
            self.__geo_std = float('inf')

    def geo_mean(self) -> float:
        """This is the geometric mean in seconds."""
        return self.__geo_mean

    def lb(self) -> float:
        """
        This is the lower bound in seconds of the one-geometric standard
        deviation interval.
        """
        return 0 if math.isnan(self.__geo_mean) else self.__geo_mean / self.__geo_std

    def ub(self) -> float:
        """
        This is the upper bound in seconds of the one-geometric standard
        deviation interval.
        """
        return float('inf') if math.isnan(self.__geo_mean) else self.__geo_mean * self.__geo_std


class _ToolRun:

    def __init__(self, run_id: int, tool: Tool, test_maker: TestFactory):
        self.__id = run_id
        self.__test_maker = test_maker
        self.__tool = tool
        self.__result = None

    def perform(self, recorder: Recorder) -> None:
        """This uses the tool to perform the action being tested."""
        label = f"run {self.__id} of {self.__test_maker.test_name()} using {self.__tool.name()}"
        recorder.notify(f"performing {label}")
        test = self.__test_maker.make_test(self.__tool)
        try:
            test.perform()
            self.__result = test.duration()
        except TestFailure as tf:
            recorder.notify(f"{label} failed: {tf}")

    def duration(self) -> Optional[float]:
        """
        This is how long it took in seconds for the tool to perform the action
        being tested.
        """
        return self.__result


class _ToolRunSet:

    def __init__(self, num_runs: int, tool: Tool, test_maker: TestFactory):
        self.__test_maker = test_maker
        self.__tool = tool
        self.__runs = [_ToolRun(run_id, tool, test_maker) for run_id in range(1, num_runs + 1)]

    def perform(self, recorder: Recorder) -> None:
        """
        This measures the performance of a tool when it performs a given action.
        """
        recorder.notify(
            f"performing {self.__test_maker.test_name()} tests using {self.__tool.name()}" )
        for run in self.__runs:
            run.perform(recorder)
        result = _TestResult([run.duration() for run in self.__runs if run.duration()])
        recorder.log(f"{self.__tool.name()}: {result.geo_mean()} [{result.lb()}, {result.ub()}] s")


class _PerformanceComparison:

    def __init__(self, num_runs: int, tools: List[Tool], test_maker: TestFactory):
        self.__test_maker = test_maker
        self.__tool_runs = [ _ToolRunSet(num_runs, tool, test_maker) for tool in tools ]

    def perform(self, recorder: Recorder) -> None:
        """
        This measures the performance of each tool when it performs a given
        action.
        """
        recorder.notify(f"performing {self.__test_maker.test_name()} tests")
        recorder.log(f"\n{self.__test_maker.test_name()} results")
        for run_set in self.__tool_runs:
            run_set.perform(recorder)


class PerformanceSuite:
    """This is the performance suite.

    A performance suite consists of a set of tools whose performance is being
    compared when performing a given set of actions.

    Parameters:
        num_runs     This is the number of times a tool will perform an action
            when measuring its performance.
        tools        This is the set of tools whose performances are being
            measured.
        test_makers  This is a set of test factories, one for each action being
            performed.
    """

    def __init__(self, num_runs: int, tools: List[Tool], test_makers: List[TestFactory]):
        self.__tests = [ _PerformanceComparison(num_runs, tools, maker) for maker in test_makers ]

    def run(self, recorder: Recorder) -> None:
        """This runs all performance tests.
        Args:
            recorder: All notifications and logs will be written to the recorder.
        """
        recorder.notify("starting performance test suite")
        for test in self.__tests:
            test.perform(recorder)
