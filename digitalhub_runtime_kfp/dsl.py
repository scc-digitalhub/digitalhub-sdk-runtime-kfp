# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import os
from contextlib import contextmanager

import digitalhub as dh
from digitalhub.runtimes.enums import RuntimeEnvVar
from digitalhub.stores.credentials.enums import CredsEnvVar
from kfp import dsl


LABEL_PREFIX = "kfp-digitalhub-runtime-"
PROJECT = os.environ.get(RuntimeEnvVar.PROJECT.value)
ENDPOINT = os.environ.get(CredsEnvVar.DHCORE_ENDPOINT.value)
WORKFLOW_IMAGE = os.environ.get(CredsEnvVar.DHCORE_WORKFLOW_IMAGE.value)


@contextmanager
def pipeline_context():
    try:
        yield PipelineContext()
    finally:
        pass


class PipelineContext:
    def step(
        self,
        name: str,
        function: str | None = None,
        workflow: str | None = None,
        action: str | None = None,
        inputs: dict | None = None,
        outputs: dict | None = None,
        parameters: dict | None = None,
        **kwargs,
    ) -> dsl.ContainerOp:
        """
        Create a KFP ContainerOp to execute a DHCore function or workflow.

        This method builds the command and output mapping for a pipeline step,
        ensuring correct argument passing and output file handling.

        Parameters
        ----------
        name : str
            Name of the KFP step.
        function : str, optional
            Name of the DHCore function to execute.
        workflow : str, optional
            Name of the DHCore workflow to execute.
        action : str, optional
            Action to execute (defaults to 'pipeline' for workflows).
        inputs : dict, optional
            Complex input parameters.
        outputs : dict, optional
            Complex output parameters.
        parameters : dict, optional
            Simple input parameters.
        kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        dsl.ContainerOp
            The constructed KFP ContainerOp.

        Raises
        ------
        RuntimeError
            If neither function nor workflow is provided, or if the specified entity is not found.
        Exception
            If an output is specified as a PipelineParam.
        """
        # Prepare properties and arguments
        props = {**kwargs}
        props = {k: v for k, v in props.items() if v is not None}

        parameters = parameters if parameters is not None else {}
        inputs = inputs if inputs is not None else {}
        outputs = outputs if outputs is not None else {}

        if not function and not workflow:
            raise RuntimeError("Either function or workflow must be provided.")

        function_object = workflow_object = None
        if function:
            function_object = dh.get_function(function, project=PROJECT)
            if function_object is None:
                raise RuntimeError(f"Function {function} not found")
        if workflow:
            workflow_object = dh.get_workflow(workflow, project=PROJECT)
            if workflow_object is None:
                raise RuntimeError(f"Workflow {workflow} not found")
            if not action:
                action = "pipeline"

        file_outputs = {"run_id": "/tmp/run_id"}
        cmd = [
            "python",
            "step.py",
            "--project",
            PROJECT,
        ]

        if function:
            cmd += ["--function", function, "--function_id", function_object.id]
        else:
            cmd += ["--workflow", workflow, "--workflow_id", workflow_object.id]

        cmd += ["--action", action, "--jsonprops", json.dumps(props)]

        # Add input parameters
        for param, val in inputs.items():
            cmd += ["-ie", f"{param}={val}"]
        for param, val in parameters.items():
            cmd += ["-iv", f"{param}={val}"]

        # Add output parameters and file outputs
        for param, val in outputs.items():
            cmd += ["-oe", f"{param}={val}"]
            if isinstance(val, dsl.PipelineParam):
                raise Exception("Invalid output specification: cannot use pipeline params")
            oname = str(val).replace(".", "_")
            file_outputs[oname] = f"/tmp/entity_{oname}"

        cop = dsl.ContainerOp(
            name=name,
            image=WORKFLOW_IMAGE,
            command=cmd,
            file_outputs=file_outputs,
        )
        cop.add_pod_label(LABEL_PREFIX + "project", PROJECT)
        if function:
            cop.add_pod_label(LABEL_PREFIX + "function", function)
            cop.add_pod_label(LABEL_PREFIX + "function_id", function_object.id)
        if workflow:
            cop.add_pod_label(LABEL_PREFIX + "workflow", workflow)
            cop.add_pod_label(LABEL_PREFIX + "workflow_id", workflow_object.id)
        cop.add_pod_label(LABEL_PREFIX + "action", action)
        return cop
