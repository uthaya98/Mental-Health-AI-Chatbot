package com.mentalhealth.demo.demo.filter;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import org.springframework.web.server.WebFilter;
import org.springframework.web.server.WebFilterChain;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;
import java.util.List;

@Component
public class JwtAuthenticationFilter implements WebFilter {

    // ✅ All PUBLIC endpoints (single source of truth)
    private static final List<String> PUBLIC_PATHS = List.of(

            // 🔓 Swagger / OpenAPI
            "/swagger-ui",
            "/v3/api-docs",
            "/openapi.json",
            "/api/users/docs",
            "/api/docs",
            "/api/users/openapi.json",

            // 🔓 User auth
            "/api/users/login",
            "/api/users/register",

            // 🔓 Public APIs (for now)
            "/api/chat",
            "/api/sessions",
            "/api/health/**",

            // 🔓 Actuator
            "/actuator"
    );

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, WebFilterChain chain) {

        String path = exchange.getRequest().getPath().value();
        String method = exchange.getRequest().getMethod() != null
                ? exchange.getRequest().getMethod().name()
                : "";

        // ✅ 1. Always allow CORS preflight
        if ("OPTIONS".equalsIgnoreCase(method)) {
            return chain.filter(exchange);
        }

        // ✅ 2. Allow public paths
        if (PUBLIC_PATHS.stream().anyMatch(path::startsWith)) {
            return chain.filter(exchange);
        }

        // 🔐 3. Require JWT for everything else
        String authHeader = exchange.getRequest()
                .getHeaders()
                .getFirst(HttpHeaders.AUTHORIZATION);

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return unauthorizedJson(exchange);
        }

        // 🔐 TODO (later):
        // jwtUtil.validateToken(authHeader.substring(7));

        return chain.filter(exchange);
    }

    private Mono<Void> unauthorizedJson(ServerWebExchange exchange) {

        exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
        exchange.getResponse().getHeaders().setContentType(MediaType.APPLICATION_JSON);
        exchange.getResponse().getHeaders().setCacheControl("no-store");

        byte[] body = """
            {
              "error": "UNAUTHORIZED",
              "message": "Missing or invalid Authorization header"
            }
            """.getBytes(StandardCharsets.UTF_8);

        return exchange.getResponse()
                .writeWith(Mono.just(
                        exchange.getResponse()
                                .bufferFactory()
                                .wrap(body)
                ));
    }
}
