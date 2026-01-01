package com.mentalhealth.demo.demo.controller;

import com.mentalhealth.demo.demo.auth.AuthClient;
import com.mentalhealth.demo.demo.auth.JwtUtil;
import com.mentalhealth.demo.demo.model.AuthRequest;
import com.mentalhealth.demo.demo.model.AuthResponse;
import com.mentalhealth.demo.demo.auth.AuthClient.PythonAuthResponse;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/users")
public class AuthController {

    private static final Logger log =
            LoggerFactory.getLogger(AuthController.class);

    private final JwtUtil jwtUtil;
    private final AuthClient authClient;

    public AuthController(JwtUtil jwtUtil, AuthClient authClient) {
        this.jwtUtil = jwtUtil;
        this.authClient = authClient;
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(
            @RequestBody AuthRequest request
    ) {
        log.info("Login request received for email={}", request.getEmail());

        // 1️⃣ Call Python backend (BLOCKING OK for MVC)
        PythonAuthResponse pythonUser;
        try {
            pythonUser = authClient
                    .login(request.getEmail(), request.getPassword())
                    .block();
        } catch (Exception e) {
            log.warn("Python auth failed", e);
            return ResponseEntity
                    .status(HttpStatus.UNAUTHORIZED)
                    .build();
        }

        if (pythonUser == null) {
            log.warn("Invalid credentials for email={}", request.getEmail());
            return ResponseEntity
                    .status(HttpStatus.UNAUTHORIZED)
                    .build();
        }

        // 2️⃣ Generate JWT (Java responsibility)
        String token = jwtUtil.generateToken(
                pythonUser.user_id(),
                pythonUser.email()
        );

        // 3️⃣ Return response to frontend
        AuthResponse response = new AuthResponse(
                pythonUser.user_id(),
                pythonUser.email(),
                token
        );

        log.info("Login successful for email={}", pythonUser.email());

        return ResponseEntity.ok(response);
    }
}
