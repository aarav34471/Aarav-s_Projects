package com.flickfinder;

import com.flickfinder.util.Database;

/**
 * Entry point of the application.
 * 
 */

public class Main {
    /**
     * The port that the server should run on.
     */
    static int port = 9000;

    /**
     * Set up a Javalin server and the database.
     * 
     * @param args The command line arguments.
     */
    public static void main(String[] args) {

        // This gives us a path to the database file, which is in the resources folder.
        final String dbPath = "src/main/resources/movies.db";

        /**
         * This sets up the database connection and starts the server.
         * In this case, we are using a connection string to connect to the database.
         * For testing, we are using an in-memory database.
         */
        Database.getInstance("jdbc:sqlite:" + dbPath);
        // start the server
        AppConfig.startServer(port);
    }
}