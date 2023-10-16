"""
Status factory module.
"""
from __future__ import annotations

import typing

from sdk.entities.artifacts.status import ArtifactStatus
from sdk.entities.base.status import State
from sdk.entities.dataitems.status import DataitemStatus
from sdk.entities.functions.status import FunctionStatus
from sdk.entities.projects.status import ProjectStatus
from sdk.entities.runs.status import RunStatus
from sdk.entities.tasks.status import TaskStatus
from sdk.entities.workflows.status import WorkflowStatus
from sdk.utils.commons import ARTF, DTIT, FUNC, PROJ, RUNS, TASK, WKFL

if typing.TYPE_CHECKING:
    from sdk.entities.base.status import Status


class StatusBuilder:
    """
    Status factory class.
    """

    def __init__(self):
        """
        Constructor.
        """
        self._modules = {}

    def register(self, module: str, status: Status) -> None:
        """
        Register status.

        Parameters
        ----------
        module: str
            module name.
        status: Status
            Status object.

        Returns
        -------
        None
        """
        self._modules[module] = status

    def build(self, module: str, **kwargs) -> Status:
        """
        Build entity status object.

        Parameters
        ----------
        module: str
            module name.
        **kwargs
            Keyword arguments.

        Returns
        -------
        Status
            An entity status object.
        """
        if module not in self._modules:
            raise ValueError(f"Invalid module name: {module}")
        kwargs = self._parse_arguments(**kwargs)
        return self._modules[module](**kwargs)

    @staticmethod
    def _parse_arguments(**kwargs) -> dict:
        """
        Parse keyword arguments and add default values.

        Parameters
        ----------
        **kwargs
            Keyword arguments.

        Returns
        -------
        dict
            Keyword arguments with default values.
        """
        state = kwargs.get("state")
        if state is None:
            kwargs["state"] = State.CREATED.value
        else:
            if kwargs["state"] not in State.__members__:
                raise ValueError(f"Invalid state: {state}")
        return kwargs


def build_status(module: str, **kwargs) -> Status:
    """
    Wrapper for StatusBuilder.build.

    Parameters
    ----------
    module: str
        module name.
    **kwargs
        Keyword arguments.

    Returns
    -------
    Status
        An entity status object.
    """
    return status_builder.build(module, **kwargs)


status_builder = StatusBuilder()
status_builder.register(ARTF, ArtifactStatus)
status_builder.register(DTIT, DataitemStatus)
status_builder.register(FUNC, FunctionStatus)
status_builder.register(PROJ, ProjectStatus)
status_builder.register(RUNS, RunStatus)
status_builder.register(TASK, TaskStatus)
status_builder.register(WKFL, WorkflowStatus)
