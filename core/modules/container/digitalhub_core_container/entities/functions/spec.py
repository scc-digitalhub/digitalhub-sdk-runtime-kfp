"""
Function Conatiner specification module.
"""
from __future__ import annotations

from pydantic import validator
from digitalhub_core.entities.functions.spec import FunctionParams, FunctionSpec


class FunctionSpecContainer(FunctionSpec):
    """
    Specification for a Function job.
    """

    def __init__(
        self,
        image: str | None = None,
        base_image: str | None = None,
        command: str | None = None,
        args: list[str] | None = None,
    ) -> None:
        """
        Constructor.
        """
        super().__init__()

        self.image = image
        self.base_image = base_image
        self.command = command
        self.args = args


class FunctionParamsContainer(FunctionParams):
    """
    Function container parameters model.
    """

    image: str = None
    """Name of the Function's container image."""

    base_image: str = None
    """Function's base container image."""

    command: str = None
    """Command to run inside the container."""

    args: list[str] = None
    """Arguments to pass to the entrypoint."""

    @validator("base_image", always=True)
    def image_validator(cls, v, values):
        if (values["image"] is None) == (v is None):
            raise ValueError("Must provide either 'image' or 'base_image'.")
        return v
