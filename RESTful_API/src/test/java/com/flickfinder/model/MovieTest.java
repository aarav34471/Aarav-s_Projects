package com.flickfinder.model;

import static org.junit.jupiter.api.Assertions.assertEquals;


import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Test for the Movie Model.
 * 
 * 
 */
public class MovieTest {

	/**
	 * The movie object to be tested.
	 */
	private Movie movie;

	/**
	 * Set up the movie object before each test.
	 *
	 */
	@BeforeEach
	public void setUp() {
		movie = new Movie(1, "The Matrix", 1999);
	}

	/**
	 * Test the movie object is created with the correct values.
	 */
	@Test
	public void testMovieCreated() {
		assertEquals(1, movie.getId());
		assertEquals("The Matrix", movie.getTitle());
		assertEquals(1999, movie.getYear());
	}

	/**
	 * Test the movie object is created with the correct values.
	 */
	@Test
	public void testMovieSetters() {
		movie.setId(2);
		movie.setTitle("The Matrix Reloaded");
		movie.setYear(2003);
		assertEquals(2, movie.getId());
		assertEquals("The Matrix Reloaded", movie.getTitle());
		assertEquals(2003, movie.getYear());
	}
}
