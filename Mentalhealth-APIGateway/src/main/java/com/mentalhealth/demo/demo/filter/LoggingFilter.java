package com.mentalhealth.demo.demo.filter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import org.springframework.web.server.WebFilter;
import org.springframework.web.server.WebFilterChain;
import reactor.core.publisher.Mono;


@Component
public class LoggingFilter implements WebFilter {

    private static final Logger log = LoggerFactory.getLogger(LoggingFilter.class);

    public Mono<Void> filter(ServerWebExchange exchange, WebFilterChain chain){
        long startTime = System.currentTimeMillis();

        ServerHttpRequest request = exchange.getRequest();
        ServerHttpResponse response = exchange.getResponse();

        String method = request.getMethod().name();
        String path = request.getURI().getPath();

        String userId = request.getHeaders().getFirst("X-User-Id");
        String email = request.getHeaders().getFirst("X-User-Email");

        log.info(
                "Incoming Request | Method={} path={} userId={}",
                method,
                path,
                userId != null ? userId : "ANONYMOUS"
        );

        return chain.filter(exchange)
                .doOnSuccess(unused -> logResponse(response, method, path, userId, email, startTime))
                .doOnError(error -> logError(error, method, path, userId));
    }

    private void logResponse(
            ServerHttpResponse response,
            String method,
            String path,
            String userId,
            String email,
            long starttime
    ){
        long duration = System.currentTimeMillis() - starttime;
        int statuscode = response.getStatusCode() != null ? response.getStatusCode().value() : 500;
        log.info(
                "Outgoing Response | method={} path={} status={} userId={} duration={}ms",
                method,
                path,
                statuscode,
                userId != null ? userId : "ANONYMOUS",
                duration
        );

    }

    private void logError(
            Throwable error,
            String method,
            String path,
            String userId
    ){
        log.error(
                "Request Failed | method={} path={} userId={} error={}",
                method,
                path,
                userId != null ? userId : "anonymous",
                error.getMessage(),
                error
        );
    }
}
