from __future__ import annotations

import typing

from digitalhub.entities.run._base.entity import Run

if typing.TYPE_CHECKING:
    from digitalhub_runtime_dbt.entities.run.dbt_run.spec import RunSpecDbtRun
    from digitalhub_runtime_dbt.entities.run.dbt_run.status import RunStatusDbtRun

    from digitalhub.entities._base.entity.metadata import Metadata
    from digitalhub.entities._base.material.entity import MaterialEntity


class RunDbtRun(Run):
    """
    RunDbtRun class.
    """

    def __init__(
        self,
        project: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: RunSpecDbtRun,
        status: RunStatusDbtRun,
        user: str | None = None,
    ) -> None:
        super().__init__(project, uuid, kind, metadata, spec, status, user)

        self.spec: RunSpecDbtRun
        self.status: RunStatusDbtRun

    def _setup_execution(self) -> None:
        """
        Setup run execution.

        Returns
        -------
        None
        """
        self.refresh()
        self.spec.inputs = self.inputs(as_dict=True)

    def inputs(self, as_dict: bool = False) -> list[dict]:
        """
        Get inputs passed in spec as objects or as dictionaries.

        Parameters
        ----------
        as_dict : bool
            If True, return inputs as dictionaries.

        Returns
        -------
        list[dict]
            List of input objects.
        """
        return self.spec.get_inputs(as_dict=as_dict)

    def outputs(self, as_key: bool = False, as_dict: bool = False) -> dict:
        """
        Get run objects results.

        Parameters
        ----------
        as_key : bool
            If True, return results as keys.
        as_dict : bool
            If True, return results as dictionaries.

        Returns
        -------
        dict
            List of output objects.
        """
        return self.status.get_outputs(as_key=as_key, as_dict=as_dict)

    def output(self, key: str, as_key: bool = False, as_dict: bool = False) -> MaterialEntity | dict | str | None:
        """
        Get run object result by key.

        Parameters
        ----------
        key : str
            Key of the result.
        as_key : bool
            If True, return result as key.
        as_dict : bool
            If True, return result as dictionary.

        Returns
        -------
        Entity | dict | str | None
            Result.
        """
        return self.outputs(as_key=as_key, as_dict=as_dict).get(key)