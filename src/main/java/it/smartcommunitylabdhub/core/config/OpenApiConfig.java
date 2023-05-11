package it.smartcommunitylabdhub.core.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;

@Configuration
public class OpenApiConfig {
    @Bean
    public OpenAPI coreMicroserviceOpenAPI() {
        return new OpenAPI()
                .info(new Info().title("Core")
                        .description("{Piattaforma}")
                        .version("1.0"));
    }
}
