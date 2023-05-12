package it.smartcommunitylabdhub.core.models.dtos;

import java.util.Date;
import java.util.Map;
import java.util.HashMap;

import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@Builder
public class RunDTO {
    @NotNull
    private String id;

    @NotNull
    private String project;

    @NotNull
    private String name;

    @NotNull
    private String type;

    @Builder.Default
    private Map<String, Object> body = new HashMap<>();

    private Date created;

    private Date updated;

    private String state;
}
