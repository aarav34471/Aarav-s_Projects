package com.flickfinder.util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

/**
 * A class to seed an in-memory database with tables and data for testing
 * purposes.
 * Notice how we work with a limited number of movies, people, stars, directors,
 * and ratings.
 * This is so we can rationalise about the responses we expect from the
 * database.
 * 
 * You should not need to modify this file.
 *
 */
public class Seeder {

	/**
	 * The connection to the database.
	 * 
	 */
	Connection conn;

	/**
	 * The URL of the database.
	 */
	String url;

	/**
	 * Constructs a Seeder object and initializes the connection to the database.
	 * You may want to add further records to support your testing; however, this
	 * is optional.
	 * 
	 * @param url
	 */
	public Seeder(String url) {
		this.url = url;
		try {
			this.conn = DriverManager.getConnection(url);
			createTables();
		} catch (SQLException e) {
			e.printStackTrace();
		}

	}

	/**
	 * Creates the tables and inserts data into the database.
	 */
	public void createTables() {
		try {

			Statement stmt = conn.createStatement();
			stmt.execute("DROP TABLE IF EXISTS stars");
			stmt.execute("DROP TABLE IF EXISTS directors");
			stmt.execute("DROP TABLE IF EXISTS people");
			stmt.execute("DROP TABLE IF EXISTS movies");
			stmt.execute("DROP TABLE IF EXISTS ratings");

			String createMoviesTable = "CREATE TABLE movies (" +
					"  id INTEGER," +
					"  title TEXT NOT NULL," +
					"  year NUMERIC," +
					"  PRIMARY KEY(id)" +
					");";

			String createStarsTable = "CREATE TABLE stars (" +
					"  movie_id INTEGER NOT NULL," +
					"  person_id INTEGER NOT NULL," +
					"  FOREIGN KEY(movie_id) REFERENCES movies(id)," +
					"  FOREIGN KEY(person_id) REFERENCES people(id)" +
					");";

			String createDirectorsTable = "CREATE TABLE directors (" +
					"  movie_id INTEGER NOT NULL," +
					"  person_id INTEGER NOT NULL," +
					"  FOREIGN KEY(movie_id) REFERENCES movies(id)," +
					"  FOREIGN KEY(person_id) REFERENCES people(id)" +
					");";

			String createRatingsTable = "CREATE TABLE ratings (" +
					"  movie_id INTEGER NOT NULL," +
					"  rating REAL NOT NULL," +
					"  votes INTEGER NOT NULL," +
					"  FOREIGN KEY(movie_id) REFERENCES movies(id)" +
					");";

			String createPeopleTable = "CREATE TABLE people (" +
					"  id INTEGER," +
					"  name TEXT NOT NULL," +
					"  birth NUMERIC," +
					"  PRIMARY KEY(id)" +
					");";

			stmt.execute(createPeopleTable);
			stmt.execute(createMoviesTable);
			stmt.execute(createRatingsTable);
			stmt.execute(createDirectorsTable);
			stmt.execute(createStarsTable);
			// Inserting into movies
			stmt.execute("INSERT INTO movies (id, title, year) VALUES(1, 'The Shawshank Redemption', 1994)");
			stmt.execute("INSERT INTO movies (id, title, year) VALUES(2, 'The Godfather', 1972)");
			stmt.execute("INSERT INTO movies (id, title, year) VALUES(3, 'The Godfather: Part II', 1974)");
			stmt.execute("INSERT INTO movies (id, title, year) VALUES(4, 'The Dark Knight', 2008)");
			stmt.execute("INSERT INTO movies (id, title, year) VALUES(5, '12 Angry Men', 1957)");

			// Inserting into people
			stmt.execute("INSERT INTO people (id, name, birth) VALUES(1, 'Tim Robbins', '1958-10-16')");
			stmt.execute("INSERT INTO people (id, name, birth) VALUES(2, 'Morgan Freeman', '1937-06-01')");
			stmt.execute("INSERT INTO people (id, name, birth) VALUES(3, 'Christopher Nolan', '1970-07-30')");
			stmt.execute("INSERT INTO people (id, name, birth) VALUES(4, 'Al Pacino', '1940-04-25')");
			stmt.execute("INSERT INTO people (id, name, birth) VALUES(5, 'Henry Fonda', '1905-05-16')");

			// Inserting into stars
			stmt.execute("INSERT INTO stars (movie_id, person_id) VALUES(1, 1)");
			stmt.execute("INSERT INTO stars (movie_id, person_id) VALUES(1, 2)");
			stmt.execute("INSERT INTO stars (movie_id, person_id) VALUES(2, 4)");
			stmt.execute("INSERT INTO stars (movie_id, person_id) VALUES(3, 4)");
			stmt.execute("INSERT INTO stars (movie_id, person_id) VALUES(5, 5)");

			// Inserting into directors
			stmt.execute("INSERT INTO directors (movie_id, person_id) VALUES(1, 3)");
			stmt.execute("INSERT INTO directors (movie_id, person_id) VALUES(2, 3)");
			stmt.execute("INSERT INTO directors (movie_id, person_id) VALUES(3, 3)");
			stmt.execute("INSERT INTO directors (movie_id, person_id) VALUES(4, 3)");
			stmt.execute("INSERT INTO directors (movie_id, person_id) VALUES(5, 3)");

			// Inserting into ratings
			stmt.execute("INSERT INTO ratings (movie_id, rating, votes) VALUES (1, 9.3, 2200000)");
			stmt.execute("INSERT INTO ratings (movie_id, rating, votes) VALUES (2, 9.2, 1500000)");
			stmt.execute("INSERT INTO ratings (movie_id, rating, votes) VALUES (3, 9.0, 1000000)");
			stmt.execute("INSERT INTO ratings (movie_id, rating, votes) VALUES (4, 8.8, 2000000)");
			stmt.execute("INSERT INTO ratings (movie_id, rating, votes) VALUES (5, 8.9, 500000)");

		} catch (SQLException e) {
			e.printStackTrace();
		}
	}

	/**
	 * Returns the connection to the database.
	 * 
	 * @return the connection to the database
	 */
	public Connection getConnection() {
		return this.conn;
	}

	/**
	 * Closes the connection to the database.
	 */
	public void closeConnection() {
		try {
			conn.close();
		} catch (SQLException e) {
			e.printStackTrace();
		}
	}

	/**
	 * Returns the URL of the database.
	 * 
	 * @return the URL of the database
	 */
	public String getUrl() {
		return url;
	}

}