package it.smartcommunitylabdhub.core.components.runnables.pollers.workflows.functions;

import java.util.Map;

import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class BaseWorkflowBuilder {
    ParameterizedTypeReference<Map<String, Object>> responseType;
    RestTemplate restTemplate;

    public BaseWorkflowBuilder() {
        this.restTemplate = new RestTemplate();
        this.responseType = new ParameterizedTypeReference<Map<String, Object>>() {
        };
    }

}