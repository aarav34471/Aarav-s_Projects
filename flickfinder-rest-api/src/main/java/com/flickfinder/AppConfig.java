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
 *
 */

public class AppConfig {

	/**
	 * Sets up the routes and the static files location.
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

		PersonDAO personDao = new PersonDAO();
		PersonController personController = new PersonController(personDao);

		app.get("/movies/", movieController::getAllMovies);
		app.get("/movies/{id}", movieController::getMovieById);
		app.get("/movies/{id}/stars", movieController::getPeopleByMovieId);

		app.get("/people/", personController::getAllPeople);
		app.get("/people/{id}", personController::getPersonById);
		app.get("/people/{id}/movies", personController::getMoviesStarringPerson);

		return app;

	}

}
