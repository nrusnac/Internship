package com.example.demo;

public final class Greeting {

    private Greeting() {
    }

    public static String greet(String name) {
        if (name == null || name.isBlank()) {
            return "Hello, world!";
        }
        return "Hello, " + name.strip() + "!";
    }

    public static String asJson(String name) {
        return "{\"message\":\"" + greet(name) + "\"}";
    }
}
