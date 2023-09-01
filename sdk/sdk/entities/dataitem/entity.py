"""
Dataitem module.
"""
from __future__ import annotations

import typing

from sdk.entities.base.entity import Entity
from sdk.entities.dataitem.metadata import build_metadata
from sdk.entities.dataitem.spec.builder import build_spec
from sdk.entities.utils.utils import get_uiid
from sdk.utils.api import DTO_DTIT, api_ctx_create, api_ctx_update
from sdk.utils.exceptions import EntityError
from sdk.utils.factories import get_context, get_default_store, get_store
from sdk.utils.file_utils import clean_all, get_dir
from sdk.utils.uri_utils import get_extension, map_uri_scheme

if typing.TYPE_CHECKING:
    import pandas as pd
    from sdk.entities.dataitem.metadata import DataitemMetadata
    from sdk.entities.dataitem.spec.builder import DataitemSpec


class Dataitem(Entity):
    """
    A class representing a dataitem.
    """

    def __init__(
        self,
        project: str,
        name: str,
        kind: str | None = None,
        metadata: DataitemMetadata | None = None,
        spec: DataitemSpec | None = None,
        local: bool = False,
        embedded: bool = False,
        uuid: str | None = None,
        **kwargs,
    ) -> None:
        """
        Initialize the Dataitem instance.

        Parameters
        ----------
        project : str
            Name of the project.
        name : str
            Name of the object.
        uuid : str
            UUID.
        kind : str
            Kind of the object.
        metadata : DataitemMetadata
            Metadata of the object.
        spec : DataitemSpec
            Specification of the object.
        local: bool
            If True, run locally.
        embedded: bool
            If True, embed object in backend.
        **kwargs
            Keyword arguments.
        """
        super().__init__()
        self.project = project
        self.name = name
        self.id = get_uiid(uuid=uuid)
        self.kind = kind if kind is not None else "table"
        self.metadata = metadata if metadata is not None else build_metadata(name=name)
        self.spec = spec if spec is not None else build_spec(self.kind, **{})
        self.embedded = embedded

        # Set new attributes
        self._any_setter(**kwargs)

        # Private attributes
        self._local = local
        self._context = get_context(self.project)

        # Set key in spec store://<project>/dataitems/<kind>/<name>:<uuid>
        self.spec.key = (
            f"store://{self.project}/dataitems/{self.kind}/{self.name}:{self.id}"
        )

    #############################
    #  Save / Export
    #############################

    def save(self, uuid: str | None = None) -> dict:
        """
        Save dataitem into backend.

        Parameters
        ----------
        uuid : str
            Specify uuid for the dataitem to update

        Returns
        -------
        dict
            Mapping representation of Dataitem from backend.
        """
        if self._local:
            raise EntityError("Use .export() for local execution.")

        obj = self.to_dict()

        if uuid is None:
            api = api_ctx_create(self.project, DTO_DTIT)
            return self._context.create_object(obj, api)

        self.id = uuid
        api = api_ctx_update(self.project, DTO_DTIT, self.name, uuid)
        return self._context.update_object(obj, api)

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
            else f"dataitem_{self.project}_{self.name}.yaml"
        )
        self._export_object(filename, obj)

    #############################
    #  Dataitem Methods
    #############################

    def as_df(self, file_format: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Read dataitem as a pandas DataFrame. If the dataitem is not local, it will be downloaded
        to a temporary folder and deleted after the method is executed. If no file_format is passed,
        the function will try to infer it from the dataitem.spec.path attribute.
        The path of the dataitem is specified in the spec attribute, and must be a store aware path.
        If the dataitem is stored on an s3 bucket, the path must be s3://<bucket>/<path_to_dataitem>.
        If the dataitem is stored on a database (Postgres is the only one supported), the path must
        be sql://postgres/<database>/<schema>/<table/view>.

        Parameters
        ----------
        file_format : str
            Format of the file. (Supported csv and parquet).
        **kwargs
            Keyword arguments.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame.
        """
        if self.spec.path is None:
            raise EntityError("Path is not specified.")

        store = get_store(self.spec.path)
        tmp_path = False

        # Check file format
        extension = self._get_extension(self.spec.path, file_format)

        # Download dataitem if not local
        if not self._check_local(self.spec.path):
            path = store.download(self.spec.path)
            tmp_path = True
        else:
            path = self.spec.path

        df = store.read_df(path, extension, **kwargs)
        if tmp_path:
            clean_all(get_dir(path))

        return df

    def write_df(
        self, df: pd.DataFrame, target_path: str | None = None, **kwargs
    ) -> str:
        """
        Write pandas DataFrame as parquet.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to write.
        target_path : str
            Path to write the dataframe to
        **kwargs
            Keyword arguments.

        Returns
        -------
        str
            Path to the written dataframe.
        """
        store = get_default_store()
        return store.write_df(df, target_path, **kwargs)

    #############################
    #  Helper Methods
    #############################

    @staticmethod
    def _check_local(path: str) -> bool:
        """
        Check if path is local.

        Parameters
        ----------
        path : str
            Path to check.

        Returns
        -------
        bool
            True if local, False otherwise.
        """
        return map_uri_scheme(path) == "local"

    @staticmethod
    def _get_extension(path: str, file_format: str | None = None) -> str:
        """
        Get extension of path.

        Parameters
        ----------
        path : str
            Path to get extension from.
        file_format : str
            File format.

        Returns
        -------
        str
            File extension.

        Raises
        ------
        EntityError
            If file format is not supported.
        """
        if file_format is not None:
            return file_format
        scheme = map_uri_scheme(path)
        if scheme == "sql":
            return "parquet"
        ext = get_extension(path)
        if ext is None:
            raise EntityError(
                "Unknown file format. Only csv and parquet are supported."
            )
        return ext

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
    def from_dict(cls, obj: dict) -> "Dataitem":
        """
        Create object instance from a dictionary.

        Parameters
        ----------
        obj : dict
            Dictionary to create object from.

        Returns
        -------
        Dataitem
            Dataitem instance.
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
        name = obj.get("name")
        if project is None or name is None:
            raise EntityError("Project or name are not specified.")

        # Optional fields
        uuid = obj.get("id")
        kind = obj.get("kind", "dataitem")
        embedded = obj.get("embedded")

        # Build metadata and spec
        spec = obj.get("spec")
        spec = spec if spec is not None else {}
        spec = build_spec(kind=kind, **spec)
        metadata = obj.get("metadata", {"name": name})
        metadata = build_metadata(**metadata)

        return {
            "project": project,
            "name": name,
            "kind": kind,
            "uuid": uuid,
            "metadata": metadata,
            "spec": spec,
            "embedded": embedded,
        }


def dataitem_from_parameters(
    project: str,
    name: str,
    description: str = "",
    kind: str = "table",
    key: str | None = None,
    path: str | None = None,
    raw_code: str | None = None,
    compiled_code: str | None = None,
    local: bool = False,
    embedded: bool = False,
    uuid: str | None = None,
) -> Dataitem:
    """
    Create a new object instance.

    Parameters
    ----------
    project : str
        Name of the project.
    name : str
        Identifier of the dataitem.
    description : str
        Description of the dataitem.
    kind : str
        The type of the dataitem.
    key : str
        Representation of the dataitem, e.g. store://etc.
    path : str
        Path to the dataitem on local file system or remote storage.
    raw_code : str
        Raw code of the dataitem.
    compiled_code : str
        Compiled code of the dataitem.
    local : bool
        Flag to determine if object has local execution.
    embedded : bool
        Flag to determine if object must be embedded in project.
    uuid : str
        UUID.

    Returns
    -------
    Dataitem
        Dataitem object.
    """
    meta = build_metadata(name=name, description=description)
    spec = build_spec(kind, key=key, path=path)
    return Dataitem(
        project=project,
        name=name,
        kind=kind,
        metadata=meta,
        spec=spec,
        local=local,
        embedded=embedded,
        uuid=uuid,
    )


def dataitem_from_dict(obj: dict) -> Dataitem:
    """
    Create dataitem from dictionary.

    Parameters
    ----------
    obj : dict
        Dictionary to create dataitem from.

    Returns
    -------
    Dataitem
        Dataitem object.
    """
    return Dataitem.from_dict(obj)