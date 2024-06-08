package com.flickfinder.dao;

import static org.junit.jupiter.api.Assertions.assertEquals;

import static org.junit.jupiter.api.Assertions.fail;

import java.sql.SQLException;
import java.util.List;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import com.flickfinder.model.Movie;
import com.flickfinder.model.Person;
import com.flickfinder.util.Database;
import com.flickfinder.util.Seeder;


class PersonDAOTest {


	private PersonDAO personDAO;


	Seeder seeder;

	@BeforeEach
	void setUp() {
		var url = "jdbc:sqlite::memory:";
		seeder = new Seeder(url);
		Database.getInstance(seeder.getConnection());
		personDAO = new PersonDAO();

	}


	@Test
	void testGetAllPeople() {
		try {
			List<Person> people = personDAO.getAllPeople();
			assertEquals(5, people.size());
		} catch (SQLException e) {
			fail("SQLException thrown");
			e.printStackTrace();
		}
	}
	
	void testGetAllPeopleLimit() {
		try {
			List<Person> people = personDAO.getAllPeople(2);
			assertEquals(2, people.size());
		} catch (SQLException e) {
			fail("SQLException thrown");
			e.printStackTrace();
		}
	}


	@Test
	void testGetPersonById() {
		Person person;
		try {
			person = personDAO.getPersonByID(5);
			assertEquals("Henry Fonda", person.getName());
		} catch (SQLException e) {
			fail("SQLException thrown");
			e.printStackTrace();
		}
	}
	
	void testMovieByStarId() {
		List<Movie> movies;
		try {
			movies = personDAO.getMovieByStarId(4);
			assertEquals(2, movies.size());
		} catch (SQLException e) {
			fail("SQLException thrown");
			e.printStackTrace();
		}
	}

	
	@Test
	void testGetPersonByIdInvalidId() {


		try {
			Person person = personDAO.getPersonByID(500);
			assertEquals(null, person);
		} catch (SQLException e) {
			fail("SQLException thrown");
			e.printStackTrace();
		}

	}

	@AfterEach
	void tearDown() {
		seeder.closeConnection();
	}

}