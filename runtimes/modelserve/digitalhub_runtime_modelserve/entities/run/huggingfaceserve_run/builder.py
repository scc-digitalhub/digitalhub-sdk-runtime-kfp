from __future__ import annotations

from digitalhub_runtime_modelserve.entities._base.runtime_entity.builder import RuntimeEntityBuilderHuggingfaceserve
from digitalhub_runtime_modelserve.entities.run.huggingfaceserve_run.entity import RunHuggingfaceserveRun
from digitalhub_runtime_modelserve.entities.run.huggingfaceserve_run.spec import (
    RunSpecHuggingfaceserveRun,
    RunValidatorHuggingfaceserveRun,
)
from digitalhub_runtime_modelserve.entities.run.huggingfaceserve_run.status import RunStatusHuggingfaceserveRun

from digitalhub.entities.run._base.builder import RunBuilder


class RunHuggingfaceserveRunBuilder(RunBuilder, RuntimeEntityBuilderHuggingfaceserve):
    """
    RunHuggingfaceserveRunBuilder runer.
    """

    ENTITY_CLASS = RunHuggingfaceserveRun
    ENTITY_SPEC_CLASS = RunSpecHuggingfaceserveRun
    ENTITY_SPEC_VALIDATOR = RunValidatorHuggingfaceserveRun
    ENTITY_STATUS_CLASS = RunStatusHuggingfaceserveRun
    ENTITY_KIND = "huggingfaceserve+run"