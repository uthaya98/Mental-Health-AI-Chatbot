package com.mentalhealth.demo.demo.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public class AuthResponse {

    @JsonProperty("access_token")
    private String accessToken;

    @JsonProperty("user_id")
    private String userId;

    private String email;

    public AuthResponse() {}

    public AuthResponse(String userId, String email, String accessToken){
        this.userId = userId;
        this.email = email;
        this.accessToken = accessToken;
    }

    public String getAccessToken() {
        return accessToken;
    }

    public void setAccessToken(String accessToken) {
        this.accessToken = accessToken;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }
}
