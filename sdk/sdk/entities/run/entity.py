"""
Run module.
"""
from __future__ import annotations

import typing

from sdk.entities.artifact.crud import get_artifact_from_key
from sdk.entities.base.entity import Entity
from sdk.entities.dataitem.crud import get_dataitem_from_key
from sdk.entities.run.spec.builder import build_spec
from sdk.entities.utils.utils import get_uiid
from sdk.utils.api import DTO_RUNS, api_base_create, api_base_delete, api_base_read
from sdk.utils.exceptions import EntityError
from sdk.utils.factories import get_context

if typing.TYPE_CHECKING:
    from sdk.entities.run.spec.builder import RunSpec
    from sdk.entities.artifact.entity import Artifact
    from sdk.entities.dataitem.entity import Dataitem


class Run(Entity):
    """
    A class representing a run.
    """

    def __init__(
        self,
        project: str,
        task_id: str,
        task: str | None = None,
        spec: RunSpec | None = None,
        local: bool = False,
        uuid: str | None = None,
        **kwargs,
    ) -> None:
        """
        Initialize the Run instance.

        Parameters
        ----------
        project : str
            Name of the project.
        uuid : str
            UUID.
        task_id : str
            Identifier of the task.
        spec : RunSpec
            Specification of the object.
        local: bool
            If True, run locally.
        """
        super().__init__()
        self.project = project
        self.kind = "run"
        self.id = get_uiid(uuid=uuid)
        self.task_id = task_id
        self.task = task
        self.status = {}
        self.spec = spec if spec is not None else build_spec(self.kind, **{})

        # Set new attributes
        self._any_setter(**kwargs)

        # Private attributes
        self._local = local
        self._obj_attr += ["task_id", "task", "status"]
        self._context = get_context(self.project)

    #############################
    #  Save / Export
    #############################

    def save(self, uuid: str | None = None) -> dict:
        """
        Save run into backend.

        Parameters
        ----------
        uuid : str
            Ignore this parameter.

        Returns
        -------
        dict
            Mapping representation of Run from backend.
        """
        if self._local:
            raise EntityError("Use .export() for local execution.")

        obj = self.to_dict()

        # Pop status, backend handles it
        obj.pop("status", None)

        # We only need to create the run, no need to update it
        api = api_base_create(DTO_RUNS)
        response = self._context.create_object(obj, api)

        # Set id
        id_ = response.get("id")
        if id_ is not None:
            self.id = id_

        return response

    def export(self, filename: str | None = None) -> None:
        """
        Export object as a YAML file.

        Parameters
        ----------
        filename : str
            Name of the export YAML file. If not specified, the default value is used.

        Returns
        -------
        None
        """
        obj = self.to_dict()
        filename = (
            filename
            if filename is not None
            else f"run_{self.project}_{self.task_id}_{self.id}.yaml"
        )
        self._export_object(filename, obj)

    #############################
    #  Run Methods
    #############################

    def refresh(self) -> dict:
        """
        Get run from backend.

        Returns
        -------
        dict
            Mapping representation of Run from backend.
        """
        if self._local:
            raise EntityError("Cannot refresh local run.")

        api = api_base_read(DTO_RUNS, self.id)
        return self._context.read_object(api)

    def delete(self) -> dict:
        """
        Delete run from backend.

        Returns
        -------
        dict
            Delete response from backend.
        """
        if self._local:
            raise EntityError("Cannot delete local run.")

        api = api_base_delete(DTO_RUNS, self.id)
        return self._context.delete_object(api)

    def stop(self) -> dict:
        """
        Not implemented yet.
        """
        raise NotImplementedError

    def logs(self) -> dict:
        """
        Get run's logs from backend.

        Returns
        -------
        dict
            Logs from backend.
        """
        api = api_base_read(DTO_RUNS, self.id) + "/log"
        return self._context.read_object(api)

    def get_artifacts(self, output_key: str | None = None) -> Artifact | list[Artifact]:
        """
        Get artifact(s) from backend produced by the run through its key.

        Parameters
        ----------
        output_key : str, optional
            Key of the artifact to get. If not provided, returns all artifacts.

        Returns
        -------
        Artifact | list[Artifact]
            Artifact(s) from backend.
        """
        resp = self.refresh()
        result = resp.get("status", {}).get("artifacts")
        if result is None:
            raise EntityError("Run has no result (maybe try when it finishes).")
        if output_key is not None:
            key = next(
                (r.get("id") for r in result if r.get("key") == output_key), None
            )
            if key is None:
                raise EntityError(f"No artifact found with key '{output_key}'.")
            return get_artifact_from_key(key)
        return [get_artifact_from_key(r.get("id")) for r in result]

    def get_dataitem(self, output_key: str | None = None) -> Dataitem | list[Dataitem]:
        """
        Get dataitem(s) from backend produced by the run through its key.

        Parameters
        ----------
        output_key : str, optional
            Key of the dataitem to get. If not provided, returns all dataitems.

        Returns
        -------
        Dataitem | list[Dataitem]
            Dataitem(s) from backend.
        """
        resp = self.refresh()
        result = resp.get("status", {}).get("dataitems")
        if result is None:
            raise EntityError("Run has no result (maybe try when it finishes).")
        if output_key is not None:
            key = next(
                (r.get("id") for r in result if r.get("key") == output_key), None
            )
            if key is None:
                raise EntityError(f"No dataitem found with key '{output_key}'.")
            return get_dataitem_from_key(key)
        return [get_dataitem_from_key(r.get("id")) for r in result]

    def set_status(self, status: dict) -> None:
        """
        Set run status.

        Parameters
        ----------
        status : dict
            Status to set.

        Returns
        -------
        None

        Raises
        ------
        EntityError
            If status is not a dictionary.
        """
        if not isinstance(status, dict):
            raise EntityError("Status must be a dictionary.")
        self.status = status

    #############################
    #  Getters and Setters
    #############################

    @property
    def local(self) -> bool:
        """
        Get local flag.

        Returns
        -------
        bool
            Local flag.
        """
        return self._local

    #############################
    #  Generic Methods
    #############################

    @classmethod
    def from_dict(cls, obj: dict) -> "Run":
        """
        Create object instance from a dictionary.

        Parameters
        ----------
        obj : dict
            Dictionary to create object from.

        Returns
        -------
        Run
            Self instance.
        """
        parsed_dict = cls._parse_dict(obj)
        _obj = cls(**parsed_dict)
        _obj._local = _obj._context.local
        return _obj

    @staticmethod
    def _parse_dict(obj: dict) -> dict:
        """
        Parse dictionary.

        Parameters
        ----------
        obj : dict
            Dictionary to parse.

        Returns
        -------
        dict
            Parsed dictionary.
        """

        # Mandatory fields
        project = obj.get("project")
        task_id = obj.get("task_id")
        task = obj.get("task")
        if project is None or task_id is None or task is None:
            raise EntityError("Project, task or task_id are not specified.")

        # Optional fields
        uuid = obj.get("id")
        kind = obj.get("kind", "run")

        # Build metadata and spec
        spec = obj.get("spec")
        spec = spec if spec is not None else {}
        spec = build_spec(kind=kind, **spec)

        return {
            "project": project,
            "task_id": task_id,
            "task": task,
            "kind": kind,
            "uuid": uuid,
            "spec": spec,
        }


def run_from_parameters(
    project: str,
    task_id: str,
    task: str,
    kind: str = "run",
    inputs: dict | None = None,
    outputs: list | None = None,
    parameters: dict | None = None,
    local: bool = False,
) -> Run:
    """
    Create run.

    Parameters
    ----------
    project : str
        Name of the project.
    task_id : str
        Identifier of the task associated with the run.
    task : str
        Name of the task associated with the run.
    kind : str
        The type of the run.
    inputs : dict
        Inputs of the run.
    outputs : list
        Outputs of the run.
    parameters : dict
        Parameters of the run.
    local : bool
        Flag to determine if object has local execution.
    embedded : bool
        Flag to determine if object must be embedded in project.

    Returns
    -------
    Run
        Run object.
    """
    spec = build_spec(kind, inputs=inputs, outputs=outputs, parameters=parameters)
    return Run(
        project=project,
        task_id=task_id,
        task=task,
        kind=kind,
        spec=spec,
        local=local,
    )


def run_from_dict(obj: dict) -> Run:
    """
    Create run from dictionary.

    Parameters
    ----------
    obj : dict
        Dictionary to create run from.

    Returns
    -------
    Run
        Run object.
    """
    return Run.from_dict(obj)