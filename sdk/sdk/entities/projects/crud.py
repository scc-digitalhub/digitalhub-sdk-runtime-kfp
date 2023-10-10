"""
Project operations module.
"""
from __future__ import annotations

import typing

from sdk.client.builder import get_client
from sdk.context.builder import delete_context
from sdk.entities.projects.entity import project_from_dict, project_from_parameters
from sdk.utils.api import api_base_delete, api_base_read, api_ctx_delete
from sdk.utils.commons import ARTF, DTIT, FUNC, PROJ, WKFL
from sdk.utils.exceptions import EntityError
from sdk.utils.io_utils import read_yaml

if typing.TYPE_CHECKING:
    from sdk.entities.projects.entity import Project


def create_project(**kwargs) -> Project:
    """
    Create a new project.

    Parameters
    ----------
    **kwargs
        Keyword arguments.

    Returns
    -------
    Project
        A Project instance.
    """
    return project_from_parameters(**kwargs)


def new_project(
    name: str,
    description: str | None = None,
    context: str | None = None,
    source: str | None = None,
    uuid: str | None = None,
    local: bool = False,
    **kwargs,
) -> Project:
    """
    Create a new project and an execution context.

    Parameters
    ----------
    name : str
        Name of the project.
    description : str
        The description of the project.
    context : str
        The path to the project's execution context.
    source : str
        The path to the project's source code.
    uuid : str
        UUID.
    local : bool
        Flag to determine if backend is present.

    Returns
    -------
    Project
        A Project instance.
    """
    obj = create_project(
        name=name,
        description=description,
        context=context,
        source=source,
        uuid=uuid,
        local=local,
        **kwargs,
    )
    obj.save()
    return obj


def load_project(
    name: str | None = None,
    filename: str | None = None,
) -> Project:
    """
    Load project and context from backend or file.

    Parameters
    ----------
    name : str
        Name of the project.
    filename : str
        Path to file where to load project from.

    Returns
    -------
    Project
        A Project instance with setted context.
    """
    if name is not None:
        return get_project(name)
    if filename is not None:
        return import_project(filename)
    raise EntityError("Either name or filename must be provided.")


def get_project(name: str) -> Project:
    """
    Retrieves project details from the backend.

    Parameters
    ----------
    name : str
        The name or UUID.

    Returns
    -------
    Project
        Object instance.
    """
    api = api_base_read(PROJ, name)
    obj_be = get_client().read_object(api)

    # Extract spec
    spec = {}
    spec["source"] = obj_be.get("source", None)
    spec["context"] = obj_be.get("context", "./")
    spec["functions"] = obj_be.get("functions", [])
    spec["artifacts"] = obj_be.get("artifacts", [])
    spec["workflows"] = obj_be.get("workflows", [])
    spec["dataitems"] = obj_be.get("dataitems", [])

    # Filter out spec from object
    fields = [
        "functions",
        "artifacts",
        "workflows",
        "source",
        "context",
        "metadata",
        "spec",
    ]

    # Set spec for new object and create Project instance
    obj = {k: v for k, v in obj_be.items() if k not in fields}
    obj["spec"] = spec
    return project_from_dict(obj)


def import_project(file: str) -> Project:
    """
    Import an Project object from a file using the specified file path.

    Parameters
    ----------
    file : str
        Path to the file.

    Returns
    -------
    Project
        Object instance.
    """
    obj = read_yaml(file)
    return project_from_dict(obj)


def delete_project(name: str, delete_all: bool = False) -> list[dict]:
    """
    Delete a project.

    Parameters
    ----------
    name : str
        Name of the project.

    Returns
    -------
    dict
        Response from backend.
    """
    client = get_client()
    responses = []

    # Delete all objects related to project -> must be done by backend
    if delete_all:
        for dto in [ARTF, FUNC, WKFL, DTIT]:
            api_proj = f"/api/v1/{PROJ}/{name}/{dto}"
            try:
                objs = client.read_object(api_proj)
                for obj in objs:
                    api = api_ctx_delete(name, dto, obj["name"])
                    responses.append(client.delete_object(api))
            except Exception:
                ...

    # Delete project
    try:
        api = api_base_delete(PROJ, name)
        responses.append(client.delete_object(api))
    except Exception:
        ...

    delete_context(name)

    return responses
