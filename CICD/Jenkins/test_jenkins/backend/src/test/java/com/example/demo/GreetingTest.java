package com.example.demo;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class GreetingTest {

    @Test
    void greetsByName() {
        assertEquals("Hello, Jenkins!", Greeting.greet("Jenkins"));
    }

    @Test
    void trimsWhitespace() {
        assertEquals("Hello, Jenkins!", Greeting.greet("  Jenkins  "));
    }

    @Test
    void fallsBackToWorldWhenNameMissing() {
        assertEquals("Hello, world!", Greeting.greet(null));
        assertEquals("Hello, world!", Greeting.greet("   "));
    }

    @Test
    void producesJson() {
        assertEquals("{\"message\":\"Hello, Jenkins!\"}", Greeting.asJson("Jenkins"));
    }
}
