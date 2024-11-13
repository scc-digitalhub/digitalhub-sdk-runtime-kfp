from __future__ import annotations

import time
import typing

from digitalhub.entities._base.unversioned.entity import UnversionedEntity
from digitalhub.entities._commons.enums import EntityTypes, State
from digitalhub.entities._operations.processor import processor
from digitalhub.factory.api import (
    build_runtime,
    build_spec,
    build_status,
    get_entity_type_from_kind,
    get_executable_kind,
)
from digitalhub.utils.exceptions import EntityError
from digitalhub.utils.logger import LOGGER

if typing.TYPE_CHECKING:
    from digitalhub.entities._base.entity.metadata import Metadata
    from digitalhub.entities.run._base.spec import RunSpec
    from digitalhub.entities.run._base.status import RunStatus
    from digitalhub.runtimes._base import Runtime


class Run(UnversionedEntity):
    """
    A class representing a run.
    """

    ENTITY_TYPE = EntityTypes.RUN.value

    def __init__(
        self,
        project: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: RunSpec,
        status: RunStatus,
        user: str | None = None,
    ) -> None:
        super().__init__(project, uuid, kind, metadata, spec, status, user)

        self.spec: RunSpec
        self.status: RunStatus

    ##############################
    #  Run Methods
    ##############################

    def build(self) -> None:
        """
        Build run.

        Returns
        -------
        None
        """
        executable = self._get_executable()
        task = self._get_task()
        new_spec = self._get_runtime().build(executable, task, self.to_dict())
        self.spec = build_spec(
            self.kind,
            **new_spec,
        )
        self._set_state(State.BUILT.value)
        self.save()

    def run(self) -> Run:
        """
        Run run.

        Returns
        -------
        Run
            Run object.
        """
        self.refresh()
        if self.spec.local_execution:
            if not self._is_ready_to_run():
                raise EntityError("Run is not in a state to run.")
            self._set_state(State.RUNNING.value)
            self.save(update=True)

        self._setup_execution()

        try:
            status = self._get_runtime().run(self.to_dict())
        except Exception as e:
            self.refresh()
            if self.spec.local_execution:
                self._set_state(State.ERROR.value)
            self._set_message(str(e))
            self.save(update=True)
            raise e

        self.refresh()
        if not self.spec.local_execution:
            status.pop("state", None)
        new_status = {**self.status.to_dict(), **status}
        self._set_status(new_status)
        self.save(update=True)
        return self

    def wait(self, log_info: bool = True) -> Run:
        """
        Wait for run to finish.

        Parameters
        ----------
        log_info : bool
            If True, log information.

        Returns
        -------
        Run
            Run object.
        """
        start = time.time()
        while True:
            if log_info:
                LOGGER.info(f"Waiting for run {self.id} to finish...")
            self.refresh()
            time.sleep(5)
            if self.status.state in [
                State.STOPPED.value,
                State.ERROR.value,
                State.COMPLETED.value,
            ]:
                if log_info:
                    current = time.time() - start
                    LOGGER.info(f"Run {self.id} finished in {current:.2f} seconds.")
                return self

    def logs(self) -> dict:
        """
        Get run logs.

        Returns
        -------
        dict
            Run logs.
        """
        return processor.read_run_logs(self.project, self.ENTITY_TYPE, self.id)

    def stop(self) -> None:
        """
        Stop run.

        Returns
        -------
        None
        """
        if not self.spec.local_execution:
            return processor.stop_run(self.project, self.ENTITY_TYPE, self.id)

    def resume(self) -> None:
        """
        Resume run.

        Returns
        -------
        None
        """
        if not self.spec.local_execution:
            return processor.resume_run(self.project, self.ENTITY_TYPE, self.id)

    ##############################
    #  Helpers
    ##############################

    def _setup_execution(self) -> None:
        """
        Setup run execution. In base class, nothing to do.

        Returns
        -------
        None
        """

    def _is_ready_to_run(self) -> bool:
        """
        Check if run is in a state ready for running (BUILT or STOPPED).

        Returns
        -------
        bool
            True if run is in runnable state, False otherwise.
        """
        return (self.status.state == State.BUILT.value) or (self.status.state == State.STOPPED.value)

    def _set_status(self, status: dict) -> None:
        """
        Set run status.

        Parameters
        ----------
        status : dict
            Status to set.

        Returns
        -------
        None
        """
        self.status: RunStatus = build_status(self.kind, **status)

    def _set_state(self, state: str) -> None:
        """
        Update run state.

        Parameters
        ----------
        state : str
            State to set.

        Returns
        -------
        None
        """
        self.status.state = state

    def _set_message(self, message: str) -> None:
        """
        Update run message.

        Parameters
        ----------
        message : str
            Message to set.

        Returns
        -------
        None
        """
        self.status.message = message

    def _get_runtime(self) -> Runtime:
        """
        Build runtime to build run or execute it.

        Returns
        -------
        Runtime
            Runtime object.
        """
        return build_runtime(self.kind, self.project)

    def _get_executable(self) -> dict:
        """
        Get executable object from backend. Reimplemented to avoid
        circular imports.

        Returns
        -------
        dict
            Executable (function or workflow) from backend.
        """
        exec_kind = get_executable_kind(self.kind)
        entity_type = get_entity_type_from_kind(exec_kind)
        splitted = self.spec.task.split("/")
        exec_name = splitted[-1].split(":")[0]
        exec_id = splitted[-1].split(":")[1]
        return processor.read_context_entity(
            exec_name,
            entity_type=entity_type,
            project=self.project,
            entity_id=exec_id,
        ).to_dict()

    def _get_task(self) -> dict:
        """
        Get object from backend. Reimplemented to avoid
        circular imports.

        Returns
        -------
        dict
            Task from backend.
        """
        executable_kind = get_executable_kind(self.kind)
        exec_string = f"{executable_kind}://{self.spec.task.split('://')[1]}"

        # Local backend
        if self._context().local:
            tasks = processor._list_base_entities(self._context().client, EntityTypes.TASK.value)
            for i in tasks:
                if i.get("spec").get("function") == exec_string:
                    return i
            raise EntityError("Task not found.")

        # Remote backend
        task_kind = self.spec.task.split("://")[0]
        params = {"function": exec_string, "kind": task_kind}
        return processor.list_context_entities(self.project, EntityTypes.TASK.value, params=params)[0].to_dict()
