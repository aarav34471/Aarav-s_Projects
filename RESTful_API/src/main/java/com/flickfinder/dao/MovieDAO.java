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
 * The Data Access Object for the Movie table.
 * 
 * This class is responsible for getting data from the Movies table in the
 * database.
 * 
 */
public class MovieDAO {

	/**
	 * The connection to the database.
	 */
	private final Connection connection;

	/**
	 * Constructs a SQLiteMovieDAO object and gets the database connection.
	 * 
	 */
	public MovieDAO() {
		Database database = Database.getInstance();
		connection = database.getConnection();
	}

	/**
	 * Returns a list of all movies in the database.
	 * 
	 * @return a list of all movies in the database
	 * @throws SQLException if a database error occurs
	 */

	public List<Movie> getAllMovies() throws SQLException {
		List<Movie> movies = new ArrayList<>();

		Statement statement = connection.createStatement();
		
		// I've set the limit to 10 for development purposes - you should do the same.
		ResultSet rs = statement.executeQuery("select * from movies LIMIT 10");
		
		while (rs.next()) {
			movies.add(new Movie(rs.getInt("id"), rs.getString("title"), rs.getInt("year")));
		}

		return movies;
	}
	
	public List<Movie> getAllMovies(int limit) throws SQLException {
		List<Movie> movies = new ArrayList<>();
		
		String statement = "select * from movies LIMIT ?";
		PreparedStatement ps = connection.prepareStatement(statement);
		ps.setInt(1, limit);
		ResultSet rs = ps.executeQuery();

		
		while (rs.next()) {
			movies.add(new Movie(rs.getInt("id"), rs.getString("title"), rs.getInt("year")));
		}

		return movies;
	}
	
	public List<Person> getStarById(int movieId) throws SQLException {
		
		List<Person> ppl = new ArrayList<>();
		String statment = "SELECT * FROM stars WHERE movie_id = ?";
		PreparedStatement ps = connection.prepareStatement(statment);
		ps.setInt(1, movieId);
		ResultSet rs = ps.executeQuery();
		
		
		while (rs.next()) {
			int person_id = rs.getInt("person_id");
			
			String stmt = "SELECT * FROM people WHERE id = ?";
			PreparedStatement ps2 = connection.prepareStatement(stmt);
			ps2.setInt(1, person_id);
			ResultSet rs2 = ps2.executeQuery();
			
			if (rs2.next()) {
				ppl.add(new Person(rs2.getInt("id"), rs2.getString("name"), rs2.getInt("birth")));
			}
		}
		return ppl;
		
	}

	/**
	 * Returns the movie with the specified id.
	 * 
	 * @param id the id of the movie
	 * @return the movie with the specified id
	 * @throws SQLException if a database error occurs
	 */
	public Movie getMovieById(int id) throws SQLException {

		String statement = "select * from movies where id = ?";
		PreparedStatement ps = connection.prepareStatement(statement);
		ps.setInt(1, id);
		ResultSet rs = ps.executeQuery();

		if (rs.next()) {

			return new Movie(rs.getInt("id"), rs.getString("title"), rs.getInt("year"));
		}
		
		// return null if the id does not return a movie.

		return null;

	}

}
