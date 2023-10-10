"""
Run Task specification module.
"""
from sdk.entities.tasks.spec.objects.base import TaskSpec


class TaskSpecJob(TaskSpec):
    """Task Perform specification."""

    def __init__(
        self,
        function: str,
        volumes: list[dict] | None = None,
        volume_mounts: list[dict] | None = None,
        env: list[dict] | None = None,
        resources: dict | None = None,
        **kwargs,
    ) -> None:
        """
        Constructor.

        Parameters
        ----------
        volumes : list[dict]
            The volumes of the task.
        volume_mounts : list[dict]
            The volume mounts of the task.
        env : list[dict]
            The env variables of the task.
        resources : dict
            Kubernetes resources for the task.
        """
        super().__init__(function, **kwargs)
        self.volumes = volumes if volumes is not None else []
        self.volume_mounts = volume_mounts if volume_mounts is not None else []
        self.env = env if env is not None else []
        self.resources = resources if resources is not None else {}
