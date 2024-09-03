from __future__ import annotations

from digitalhub_core.utils.exceptions import EntityError
from digitalhub_core.utils.logger import LOGGER
from digitalhub_runtime_modelserve.utils.frameworks.registry import config_function_registry


def get_function_args(action: str, root: str, model_path: str) -> None:
    """
    Get function arguments.

    Parameters
    ----------
    action : str
        The action.
    root : str
        Root path.
    model_path : str
        The model path.

    Returns
    -------
    None
    """
    try:
        config_function_registry[action](root, model_path)
    except KeyError as e:
        msg = f"Unsupported action {action} for local serving."
        LOGGER.error(msg)
        raise EntityError(msg) from e
    except Exception as e:
        msg = f"Something got wrong during function configuration. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.error(msg)
        raise EntityError(msg) from e
