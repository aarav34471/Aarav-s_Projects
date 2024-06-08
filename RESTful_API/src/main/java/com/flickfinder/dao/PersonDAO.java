package com.flickfinder.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

import com.flickfinder.model.Movie;
import com.flickfinder.model.Person;
import com.flickfinder.util.Database;

/**
 * TODO: Implement this class
 * 
 */
public class PersonDAO {
	
	private final Connection connection;
	
	public PersonDAO() {
		Database database = Database.getInstance();
		connection = database.getConnection();
	}
	
	public List<Person> getAllPeople() throws SQLException {
		List<Person> people = new ArrayList<>();
		
		Statement stmt = connection.createStatement();
		
		ResultSet rs = stmt.executeQuery("SELECT * FROM people LIMIT 50");
		
		while (rs.next()) {
			people.add(new Person(rs.getInt("id"), rs.getString("name"), rs.getInt("birth")));
			}
		
		return people;
	}
	
	public List<Person> getAllPeople(int limit) throws SQLException {
		List<Person> people = new ArrayList<>();
		
		String statement = "select * from people LIMIT ?";
		PreparedStatement ps = connection.prepareStatement(statement);
		ps.setInt(1, limit);
		ResultSet rs = ps.executeQuery();

		
		while (rs.next()) {
			people.add(new Person(rs.getInt("id"), rs.getString("name"), rs.getInt("birth")));
		}

		return people;
	}
	
	
	public Person getPersonByID(int id) throws SQLException {
		
		String statement = "SELECT * FROM people WHERE id = ?";
		PreparedStatement stmt = connection.prepareStatement(statement);
		stmt.setInt(1, id);
		ResultSet rs = stmt.executeQuery();
		
		while (rs.next()) {
			return new Person(rs.getInt("id"), rs.getString("name"), rs.getInt("birth"));
			}
		
		return null;
		
	}
	
	public List<Movie> getMovieByStarId(int starId) throws SQLException {
		
		List<Movie> movies = new ArrayList<>();
		String statment = "SELECT * FROM stars WHERE person_id = ?";
		PreparedStatement ps = connection.prepareStatement(statment);
		ps.setInt(1, starId);
		ResultSet rs = ps.executeQuery();
		
		
		while (rs.next()) {
			int movie_id = rs.getInt("movie_id");
			
			String stmt = "SELECT * FROM movies WHERE id = ?";
			PreparedStatement ps2 = connection.prepareStatement(stmt);
			ps2.setInt(1, movie_id);
			ResultSet rs2 = ps2.executeQuery();
			
			if (rs2.next()) {
				movies.add(new Movie(rs2.getInt("id"), rs2.getString("title"), rs2.getInt("year")));
			}
		}
		return movies;
		
	}
	

	
	
	
	// for the must have requirements, you will need to implement the following
		// methods:
		// - getAllPeople()
		// - getPersonById(int id)
		// you will add further methods for the more advanced tasks; however, ensure your have completed 
		// the must have requirements before you start these.  


	
}
