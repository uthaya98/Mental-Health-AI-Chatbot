package com.mentalhealth.demo.demo.auth;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.util.Date;

@Component
public class JwtUtil {

    @Value("${security.jwt.secret}")
    private String jwtSecret;

    @Value("${security.jwt.expiration}")
    private long expirationMs;

    private static final long CLOCK_SKEW_MS = 30_000;

    // ------------------------------------------------
    // Signing Key
    // ------------------------------------------------
    private Key getSigningKey() {
        return Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
    }

    // ------------------------------------------------
    // TOKEN GENERATION (MISSING BEFORE)
    // ------------------------------------------------
    public String generateToken(String userId, String email) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + expirationMs);

        return Jwts.builder()
                .setSubject(userId)
                .claim("email", email)
                .setIssuedAt(now)
                .setExpiration(expiry)
                .signWith(getSigningKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    // ------------------------------------------------
    // VALIDATION
    // ------------------------------------------------
    public boolean validateToken(String token) {
        try {
            Claims claims = getClaims(token);
            return !isExpired(claims);
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    // ------------------------------------------------
    // CLAIM ACCESSORS
    // ------------------------------------------------
    public String getUserId(String token) {
        return getClaims(token).getSubject();
    }

    public String getEmail(String token) {
        return getClaims(token).get("email", String.class);
    }

    // Optional — only use if you later add roles
    public String getRole(String token) {
        return getClaims(token).get("role", String.class);
    }

    // ------------------------------------------------
    // INTERNAL HELPERS
    // ------------------------------------------------
    private Claims getClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .setAllowedClockSkewSeconds(CLOCK_SKEW_MS / 1000)
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    private boolean isExpired(Claims claims) {
        return claims.getExpiration().before(new Date());
    }
}
