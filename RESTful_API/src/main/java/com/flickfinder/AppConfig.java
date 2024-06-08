package com.flickfinder;

import com.flickfinder.controller.MovieController;
import com.flickfinder.controller.PersonController;
import com.flickfinder.dao.MovieDAO;
import com.flickfinder.dao.PersonDAO;

import io.javalin.Javalin;
import io.javalin.http.staticfiles.Location;

/**
 * This class is used to configure the Javalin web server.
 * It sets up the routes and the static files location.
 * As you implement the remaining functionality, you will need to update this
 * class.
 * 
 */

public class AppConfig {

	/**
	 * Sets up the routes and the static files location.
	 * As you can see, the routes are currently incomplete. Depending on how far you
	 * get in the assessment, you will update some or all of the routes in this
	 * method.
	 * 
	 * @param port The port that the server should run on.
	 * @return The Javalin object that represents the running server.
	 */
	public static Javalin startServer(int port) {
		Javalin app = Javalin.create(config -> {
			config.staticFiles.add("/public", Location.CLASSPATH);
		}).start(port);

		// Set up controllers
		MovieDAO movieDao = new MovieDAO();
		MovieController movieController = new MovieController(movieDao);

		// Uncomment the following lines as you progress through the assessment.
		// PersonController personController = new PersonController();
		PersonDAO personDao = new PersonDAO();
		PersonController personController = new PersonController(personDao);

		/**
		 * Below are the routes for the application.
		 * You will need uncomment these as you progress through the assessment.
		 * Do not:
		 * - change the strings and methods passed to the get() method.
		 * - change the order of the routes. Order matters in Javalin, as the routes are
		 * pattern matched in the order they are defined.
		 * Only uncomment the routes for the functionality you have implemented.
		 */
		// app.get("/movies/ratings/{year}", movieController::getRatingsByYear);
		app.get("/movies/", movieController::getAllMovies);
		app.get("/movies/{id}", movieController::getMovieById);
		app.get("/movies/{id}/stars", movieController::getPeopleByMovieId);

		app.get("/people/", personController::getAllPeople);
		app.get("/people/{id}", personController::getPersonById);
		app.get("/people/{id}/movies", personController::getMoviesStarringPerson);

		return app;

	}

}