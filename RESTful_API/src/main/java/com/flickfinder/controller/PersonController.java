package com.flickfinder.controller;

import java.sql.SQLException;
import java.util.List;

import com.flickfinder.dao.PersonDAO;
import com.flickfinder.model.Movie;
import com.flickfinder.model.Person;

import io.javalin.http.Context;

public class PersonController {
	
	private final PersonDAO personDAO;

	public PersonController(PersonDAO personDAO) {
		super();
		this.personDAO = personDAO;
	}
	
	public void getAllPeople(Context ctx) {
		int limit = 50;
		try {
			List<Person> people = personDAO.getAllPeople();
			String strLimit = ctx.queryParam("limit");
			if (strLimit != null) {
				limit = Integer.parseInt(strLimit);
				people = personDAO.getAllPeople(limit);
			}
			ctx.json(people);
		} catch (SQLException e) {
			ctx.status(500);
			ctx.result("Database error");
			e.printStackTrace();
		}
	}
	
	
	public void getPersonById(Context ctx) {
		int id = Integer.parseInt(ctx.pathParam("id"));
		try {
			Person person = personDAO.getPersonByID(id);
			if (person == null) {
				ctx.status(404);
				ctx.result("Person not found");
				return;
			}
			ctx.json(personDAO.getPersonByID(id));
		} catch (SQLException e) {
			ctx.status(500);
			ctx.result("Database error");
			e.printStackTrace();
		}
		
		
	}
	
	public void getMoviesStarringPerson(Context ctx) {
		
		int id = Integer.parseInt(ctx.pathParam("id"));
		try {
			ctx.json(personDAO.getMovieByStarId(id));
		} catch (SQLException e) {
			ctx.status(500);
			ctx.result("Database Error");
			e.printStackTrace();
		}
		
		
	}
	

	
	// to complete the must-have requirements you need to add the following methods:
	// getAllPeople
	// getPersonById
	// you will add further methods for the more advanced tasks; however, ensure your have completed 
	// the must have requirements before you start these.  

}