package it.smartcommunitylabdhub.core.models.base.specs;

import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import it.smartcommunitylabdhub.core.models.base.interfaces.Spec;
import it.smartcommunitylabdhub.core.utils.JacksonMapper;
import lombok.Getter;
import lombok.Setter;

import java.util.HashMap;
import java.util.Map;

@Getter
@Setter
public abstract class BaseSpec implements Spec {
    private Map<String, Object> extraSpecs = new HashMap<>();

    @Override
    public <S extends T,
            T extends BaseSpec> void configure(Map<String, Object> data) {

        // Retrieve concreteSpec
        S concreteSpec = JacksonMapper.objectMapper.convertValue(
                data, JacksonMapper._extractJavaType(this.getClass()));

        configure(concreteSpec);
    }

    protected abstract <S extends T,
            T extends BaseSpec> void configure(S concreteSpec);

    @Override
    public Map<String, Object> toMap() {
        Map<String, Object> result = new HashMap<>();

        // Serialize all fields (including extraSpecs) to a JSON map
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            String json = objectMapper.writeValueAsString(this);

            // Convert the JSON string to a map
            Map<String, Object> serializedMap = objectMapper.readValue(json, new TypeReference<>() {
            });

            // Include extra properties in the result map
            result.putAll(serializedMap);
            result.putAll(extraSpecs);

            return result;
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error converting to Map", e);
        }
    }

    @JsonAnyGetter
    public Map<String, Object> getExtraSpecs() {
        return extraSpecs;
    }

    @JsonAnySetter
    public void setExtraSpecs(String key, Object value) {
        this.extraSpecs.put(key, value);
    }

}