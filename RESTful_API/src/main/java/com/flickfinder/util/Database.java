package com.flickfinder.util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * A class to handle the database connection.
 * You should not need to modify this class.
 * 
 */

public class Database {

	/**
	 * The instance of the database.
	 */
	private static Database instance;

	/**
	 * The connection to the database.
	 * This is optional as we can also
	 * pass in a connection to the database.
	 */
	Connection connection;

	private Database(String path) {
		try {
			this.connection = DriverManager.getConnection(path);
		} catch (SQLException e) {
			e.printStackTrace();
		}
	}

	/**
	 * This allows use to pass in an existing database connection.
	 * This is useful for testing.
	 * 
	 * @param connection
	 */

	private Database(Connection connection) {
		this.connection = connection;
	}

	/**
	 * Returns the instance of the database.
	 * We pass in the path to the database.
	 * This is the path to the database file.
	 * 
	 * @param path
	 * @return
	 */
	public static Database getInstance(String path) {
		if (instance == null) {
			instance = new Database(path);
		}
		return instance;
	}

	/**
	 * Returns the instance of the database. However, this methods allows us 
	 * to pass in the connection to an instance of an in-memory database.
	 * We use this for testing. Notice how we are using the same method name, overloading the above 
	 * method.
	 * 
	 * @param conn
	 * @return
	 */
	public static Database getInstance(Connection conn) {

		instance = new Database(conn);

		return instance;

	}

	/**
	 * Returns the instance of the database.
	 * notice how this method is static and does not take any parameters.
	 * This is because if we have already set the instance of the database, we 
	 * can just return the instance. There is no need to pass in the path or connection to the database.
	 * 
	 * 
	 * @return
	 */

	public static Database getInstance() {

		/**
		 * If the instance is null, we throw an IllegalStateException.
		 * This is because we need to set the instance of the database before we can use it.
		 * As we are using a singleton pattern, we only have to do this once. 
		 */
		if (instance == null) {
			throw new IllegalStateException("Database instance not set");
		}
		return instance;
	}

	/**
	 * Returns the connection to the database.
	 * 
	 * @return
	 */

	public Connection getConnection() {
		return this.connection;
	}

}
