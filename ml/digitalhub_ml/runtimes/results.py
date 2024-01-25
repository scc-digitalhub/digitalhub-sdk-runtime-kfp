"""
Run module.
"""
from __future__ import annotations

import typing

from digitalhub_data.runtimes.results import RunResultsData

if typing.TYPE_CHECKING:
    from digitalhub_core.entities.artifacts.entity import Artifact
    from digitalhub_core.entities.dataitems.entity import Dataitem


class RunResultsML(RunResultsData):
    """
    A class representing a run results.
    """

    def __init__(
        self,
        artifacts: list[Artifact],
        dataitems: list[Dataitem],
    ) -> None:
        """
        Constructor.

        Parameters
        ----------
        dataitems : list[Dataitem]
            The dataitems.
        """
        super().__init__(artifacts)
        self.dataitems = dataitems