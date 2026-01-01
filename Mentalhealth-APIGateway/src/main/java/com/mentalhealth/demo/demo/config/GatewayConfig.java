package com.mentalhealth.demo.demo.config;

import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class GatewayConfig {

    @Bean
    public RouteLocator gatewayRoutes(RouteLocatorBuilder builder) {
        return builder.routes()

                // ================= SWAGGER UI =================
                .route("python-swagger-ui", r -> r
                        .path("/api/docs", "/api/docs/**")
                        .filters(f -> f
                                .rewritePath("/api/docs(?<segment>/?.*)", "/docs${segment}")
                                .addRequestHeader("X-Debug-Gateway", "docs-route")  // ✅ Debug header
                        )
                        .uri("http://127.0.0.1:8080")
                )

                // ================= OPENAPI SCHEMA =================
                .route("python-openapi-prefixed", r -> r
                        .path("/api/openapi.json")
                        .filters(f -> f.setPath("/openapi.json"))
                        .uri("http://127.0.0.1:8080")
                )

                .route("python-openapi-direct", r -> r
                        .path("/openapi.json")
                        .uri("http://127.0.0.1:8080")
                )

                // ================= ALL API ROUTES =================
                .route("python-api", r -> r
                        .path("/api/**")
                        .filters(f -> f
                                .addRequestHeader("X-Gateway", "spring-cloud")
                        )
                        .uri("http://127.0.0.1:8080")
                )

                .build();
    }
}