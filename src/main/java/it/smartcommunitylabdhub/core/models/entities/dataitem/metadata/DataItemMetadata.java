package it.smartcommunitylabdhub.core.models.entities.dataitem.metadata;

import it.smartcommunitylabdhub.core.models.base.metadata.BaseMetadata;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
public class DataItemMetadata extends BaseMetadata {
    String name;

    String version;

    String description;

    boolean embedded;
}
