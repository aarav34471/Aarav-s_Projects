package com.flickfinder.controller;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.sql.SQLException;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import com.flickfinder.dao.PersonDAO;

import io.javalin.http.Context;

/**
 * Test for the Movie Controller.
 */

class PersonControllerTest {

	/**
	 *
	 * The context object, later we will mock it.
	 */
	private Context ctx;


	private PersonDAO personDAO;



	private PersonController personController;

	@BeforeEach
	void setUp() {
	
		personDAO = mock(PersonDAO.class);

		ctx = mock(Context.class);


		personController = new PersonController(personDAO);
	}

	/**
	 * Tests the getAllPeople method.
	 * We expect to get a list of all people in the database.
	 */

	@Test
	void testGetAllPeople() {
		personController.getAllPeople(ctx);
		try {
			verify(personDAO).getAllPeople();
		} catch (SQLException e) {
			e.printStackTrace();
		}
	}
	
	@Test
	public void getPeopleLimit() {
		try {
			when(ctx.queryParam("limit")).thenReturn("3");
			personController.getAllPeople(ctx);
			verify(personDAO).getAllPeople(3);
			
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	/**
	 * Test that the controller returns a 500 status code when a database error
	 * occurs
	 * 
	 * @throws SQLException
	 */
	@Test
	void testThrows500ExceptionWhenGetAllDatabaseError() throws SQLException {
		when(personDAO.getAllPeople()).thenThrow(new SQLException());
		personController.getAllPeople(ctx);
		verify(ctx).status(500);
	}

	/**
	 * Tests the getPersonById method.
	 * We expect to get the person with the specified id.
	 */

	@Test
	void testGetStarById() {
		when(ctx.pathParam("id")).thenReturn("1");
		personController.getPersonById(ctx);
		try {
			verify(personDAO).getPersonByID(1);
		} catch (SQLException e) {
			e.printStackTrace();
		}
	}
	
	void testGetMovieByStarId() {
		when(ctx.pathParam("id")).thenReturn("2");
		personController.getMoviesStarringPerson(ctx);
		try {
			verify(personDAO).getMovieByStarId(2);
		} catch (SQLException e) {
			e.printStackTrace();
		}
	}

	/**
	 * Test a 500 status code is returned when a database error occurs.
	 * 
	 * @throws SQLException
	 */

	@Test
	void testThrows500ExceptionWhenGetByIdDatabaseError() throws SQLException {
		when(ctx.pathParam("id")).thenReturn("1");
		when(personDAO.getPersonByID(1)).thenThrow(new SQLException());
		personController.getPersonById(ctx);
		verify(ctx).status(500);
	}

	/**
	 * Test that the controller returns a 404 status code when a person is not found
	 * or
	 * database error.
	 * 
	 * @throws SQLException
	 */

	@Test
	void testThrows404ExceptionWhenNoPersonFound() throws SQLException {
		when(ctx.pathParam("id")).thenReturn("1");
		when(personDAO.getPersonByID(1)).thenReturn(null);
		personController.getPersonById(ctx);
		verify(ctx).status(404);
	}
	
}