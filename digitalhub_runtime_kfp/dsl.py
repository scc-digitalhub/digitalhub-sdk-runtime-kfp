# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import os
from contextlib import contextmanager

import digitalhub as dh
from digitalhub.runtimes.enums import RuntimeEnvVar
from digitalhub.stores.client.dhcore.enums import DhcoreEnvVar
from kfp import dsl

LABEL_PREFIX = "kfp-digitalhub-runtime-"
PROJECT = os.environ.get(RuntimeEnvVar.PROJECT.value)
ENDPOINT = os.environ.get(DhcoreEnvVar.ENDPOINT.value)
WORKFLOW_IMAGE = os.environ.get(DhcoreEnvVar.WORKFLOW_IMAGE.value)


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
        Execute a function in DHCore.

        This function creates a KFP ContainerOp that executes a function
        or another workflow in DHCore.
        The function is executed in the context of the current project,
        which is retrieved from DHCore when the pipeline context
        is initialized.

        Parameters
        ----------
        name : str
            The name of the step in KFP.
        function : str
            The name of the function to execute. Either function or workflow must be provided.
        workflow : str
            The Args workflow to execute. Either function or workflow must be provided.
        action : str
            The name of the action to execute. May be omitted in case of workflow execution (defaulting to 'pipeline').
        inputs : dict
            A list of complex input parameters.
        outputs : dict
            A list of complex output parameters.
        parameters : dict
            A list of simple input parameters.
        kwargs : dict
            Additional keyword arguments to pass to the step.

        Returns
        -------
        dsl.ContainerOp
            A KFP ContainerOp for the step.
        """
        if kwargs is None:
            kwargs = {}
        props = {**kwargs}
        props = {k: v for k, v in props.items() if v is not None}

        parameters = {} if parameters is None else parameters
        inputs = {} if inputs is None else inputs
        outputs = {} if outputs is None else outputs

        if function is None and workflow is None:
            raise RuntimeError("Either function or workflow must be provided.")

        if function is not None:
            function_object = dh.get_function(function, project=PROJECT)
            if function_object is None:
                raise RuntimeError(f"Function {function} not found")
        elif workflow is not None:
            workflow_object = dh.get_workflow(workflow, project=PROJECT)
            if workflow_object is None:
                raise RuntimeError(f"Workflow {workflow} not found")
            if action is None:
                action = "pipeline"

        file_outputs = {"run_id": "/tmp/run_id"}

        cmd = [
            "python",
            "step.py",
            "--project",
            PROJECT,
            "--function" if function is not None else "--workflow",
            function if function is not None else workflow,
            "--function_id" if function is not None else "--workflow_id",
            function_object.id if function is not None else workflow_object.id,
            "--action",
            action,
            "--jsonprops",
            json.dumps(props),
        ]

        # complex input parameters
        for param, val in inputs.items():
            cmd += ["-ie", f"{param}={val}"]

        # simple input parameters
        for param, val in parameters.items():
            cmd += ["-iv", f"{param}={val}"]

        # complex output parameters
        for param, val in outputs.items():
            cmd += ["-oe", f"{param}={val}"]
            if isinstance(val, dsl.PipelineParam):
                raise Exception("Invalid output specification. cannot use pipeline params")
            else:
                oname = str(val)
            file_outputs[oname.replace(".", "_")] = f"/tmp/entity_{oname}"  # not using path.join to avoid windows "\"

        cop = dsl.ContainerOp(
            name=name,
            image=WORKFLOW_IMAGE,
            command=cmd,
            file_outputs=file_outputs,
        )
        cop.add_pod_label(LABEL_PREFIX + "project", PROJECT)
        if function is not None:
            cop.add_pod_label(LABEL_PREFIX + "function", function)
            cop.add_pod_label(LABEL_PREFIX + "function_id", function_object.id)
        if workflow is not None:
            cop.add_pod_label(LABEL_PREFIX + "workflow", workflow)
            cop.add_pod_label(LABEL_PREFIX + "workflow_id", workflow_object.id)
        cop.add_pod_label(LABEL_PREFIX + "action", action)
        return cop
