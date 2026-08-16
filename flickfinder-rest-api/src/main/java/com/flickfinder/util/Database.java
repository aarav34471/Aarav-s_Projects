package com.flickfinder.util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * Manages the shared database connection used by DAOs.
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
	 * Creates an instance around an existing connection, including an in-memory
	 * connection used by tests.
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
	 * Replaces the shared instance with one backed by the supplied connection.
	 *
	 * @param conn
	 * @return
	 */
	public static Database getInstance(Connection conn) {

		instance = new Database(conn);

		return instance;

	}

	/**
	 * Returns the configured shared database instance.
	 * @return
	 */

	public static Database getInstance() {

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
