"""
Task Container specification module.
"""
from __future__ import annotations

from digitalhub_core.entities.tasks.models import K8s
from digitalhub_core.entities.tasks.spec import TaskParams, TaskSpec
from digitalhub_core_container.entities.tasks.models import CorePort


class TaskSpecContainerBase(TaskSpec):
    """Task Container specification for Kubernetes."""

    def __init__(
        self,
        function: str,
        k8s: K8s | None = None,
    ) -> None:
        """
        Constructor.
        """
        super().__init__(function)
        if k8s is None:
            k8s = {}
        k8s = K8s(**k8s).dict(by_alias=True)
        self.node_selector = k8s.get("node_selector")
        self.volumes = k8s.get("volumes")
        self.resources = k8s.get("resources")
        self.affinity = k8s.get("affinity")
        self.tolerations = k8s.get("tolerations")
        self.env = k8s.get("env")
        self.secrets = k8s.get("secrets")
        self.backoff_limit = k8s.get("backoff_limit")
        self.schedule = k8s.get("schedule")
        self.replicas = k8s.get("replicas")


class TaskSpecJob(TaskSpecContainerBase):
    """Task Job specification."""

    def __init__(
        self,
        function: str,
        k8s: K8s | None = None,
    ) -> None:
        """
        Constructor.
        """
        super().__init__(function, k8s)


class TaskParamsJob(TaskParams):
    """
    TaskParamsJob model.
    """

    k8s: K8s = None
    """Kubernetes resources."""


class TaskSpecDeploy(TaskSpecContainerBase):
    """Task Deploy specification."""

    def __init__(
        self,
        function: str,
        k8s: K8s | None = None,
    ) -> None:
        """
        Constructor.
        """
        super().__init__(function, k8s)


class TaskParamsDeploy(TaskParams):
    """
    TaskParamsDeploy model.
    """

    k8s: K8s = None
    """Kubernetes resources."""


class TaskSpecServe(TaskSpecContainerBase):
    """Task Serve specification."""

    def __init__(
        self,
        function: str,
        k8s: K8s | None = None,
        service_ports: list[CorePort] = None,
        service_type: str = None,
    ) -> None:
        """
        Constructor.
        """
        super().__init__(function, k8s)
        self.service_ports = service_ports
        self.service_type = service_type


class TaskParamsServe(TaskParams):
    """
    TaskParamsServe model.
    """

    k8s: K8s = None
    """Kubernetes resources."""

    service_ports: list[CorePort] = None
    """Service ports mapper."""

    service_type: str = None
    """Service type."""


class TaskSpecBuild(TaskSpecContainerBase):
    """Task Build specification."""

    def __init__(
        self,
        function: str,
        k8s: K8s | None = None,
    ) -> None:
        """
        Constructor.
        """
        super().__init__(function, k8s)


class TaskParamsBuild(TaskParams):
    """
    TaskParamsBuild model.
    """

    k8s: K8s = None
    """Kubernetes resources."""
