package com.flickfinder.model;

import static org.junit.jupiter.api.Assertions.assertEquals;


import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;


public class PersonTest {

	private Person person;


	@BeforeEach
	public void setUp() {
		person = new Person(2, "Lauren Bacall", 1924);
	}


	@Test
	public void testMovieCreated() {
		assertEquals(2, person.getId());
		assertEquals("Lauren Bacall", person.getName());
		assertEquals(1924, person.getBirth());
	}

	@Test
	public void testMovieSetters() {
		person.setId(1);
		person.setName("Fred Astaire");
		person.setBirth(1899);
		assertEquals(1, person.getId());
		assertEquals("Fred Astaire", person.getName());
		assertEquals(1899, person.getBirth());
	}
	
	
}
