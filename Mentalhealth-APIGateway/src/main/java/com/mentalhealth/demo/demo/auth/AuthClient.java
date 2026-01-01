package com.mentalhealth.demo.demo.auth;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Component
public class AuthClient {

    private final WebClient webClient;

    public AuthClient(
            WebClient.Builder builder,
            @Value("${python.auth.base-url}") String baseUrl
    ) {
        this.webClient = builder.baseUrl(baseUrl).build();
    }

    /**
     * Calls Python backend to validate credentials.
     * Returns user info if valid, error if invalid.
     */
    public Mono<PythonAuthResponse> login(String email, String password) {
        return webClient.post()
                .uri("/users/login")
                .bodyValue(new LoginRequest(email, password))
                .retrieve()
                .bodyToMono(PythonAuthResponse.class);
    }

    // ===== DTOs =====

    public record LoginRequest(
            String email,
            String password
    ) {}

    /**
     * Response returned by Python backend
     */
    public record PythonAuthResponse(
            String user_id,
            String email
    ) {}
}
