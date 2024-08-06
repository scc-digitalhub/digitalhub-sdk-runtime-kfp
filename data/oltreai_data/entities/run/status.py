from __future__ import annotations

from oltreai_core.entities.run.status import ENTITY_FUNC, RunStatus
from oltreai_data.entities.dataitem.crud import get_dataitem
from oltreai_data.entities.entity_types import EntityTypes

ENTITY_FUNC[EntityTypes.DATAITEM.value] = get_dataitem


class RunStatusData(RunStatus):
    """
    A class representing a run status.
    """
