package com.example.demo;

import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

public class App {

    public static void main(String[] args) throws IOException {
        // Default to 8081: Jenkins itself usually occupies 8080
        int port = Integer.parseInt(System.getenv().getOrDefault("PORT", "8081"));
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);

        server.createContext("/api/hello", exchange -> {
            String name = queryParam(exchange.getRequestURI().getQuery());
            byte[] body = Greeting.asJson(name).getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().add("Content-Type", "application/json");
            exchange.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream os = exchange.getResponseBody()) {
                os.write(body);
            }
        });

        server.start();
        System.out.println("Backend listening on http://localhost:" + port + "/api/hello");
    }

    static String queryParam(String query) {
        if (query == null) {
            return null;
        }
        for (String pair : query.split("&")) {
            String[] parts = pair.split("=", 2);
            if (parts.length == 2 && parts[0].equals("name")) {
                return parts[1];
            }
        }
        return null;
    }
}
