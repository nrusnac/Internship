package com.example.demo;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import org.junit.jupiter.api.Test;

class AppTest {

    @Test
    void extractsNameFromQuery() {
        assertEquals("Jenkins", App.queryParam("name=Jenkins"));
        assertEquals("Jenkins", App.queryParam("foo=bar&name=Jenkins"));
    }

    @Test
    void returnsNullWhenNameAbsent() {
        assertNull(App.queryParam(null));
        assertNull(App.queryParam("foo=bar"));
        assertNull(App.queryParam("name"));
    }
}
