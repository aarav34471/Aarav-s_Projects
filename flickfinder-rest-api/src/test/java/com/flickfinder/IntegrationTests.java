package com.flickfinder;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItems;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import com.flickfinder.util.Database;
import com.flickfinder.util.Seeder;

import io.javalin.Javalin;

/**
 * Exercises the HTTP application against an isolated in-memory database.
 */
class IntegrationTests {

	/**
	 * The Javalin app.*
	 */
	Javalin app;

	/**
	 * The seeder object.
	 */
	Seeder seeder;

	/**
	 * The dedicated port used by the test server.
	 */
	int port = 6000;

	/**
	 * The base URL for our test application.
	 */
	String baseURL = "http://localhost:" + port;

	/**
	 * Bootstraps the application before each test.
	 */
	@BeforeEach
	void setUp() {
		var url = "jdbc:sqlite::memory:";
		seeder = new Seeder(url);
		Database.getInstance(seeder.getConnection());
		app = AppConfig.startServer(port);
	}

	/**
	 * Verifies that the collection endpoint returns the seeded movie records.
	 */

	@Test
	void retrieves_a_list_of_all_movies() {
		given().when().get(baseURL + "/movies").then().assertThat().statusCode(200).
				body("id", hasItems(1, 2, 3, 4, 5))
				.body("title", hasItems("The Shawshank Redemption", "The Godfather",
						"The Godfather: Part II", "The Dark Knight", "12 Angry Men"))
				.body("year", hasItems(1994, 1972, 1974, 2008, 1957));
	}

	@Test
	void retrieves_a_single_movie_by_id() {

		given().when().get(baseURL + "/movies/1").then().assertThat().statusCode(200).
				body("id", equalTo(1))
				.body("title", equalTo("The Shawshank Redemption"))
				.body("year", equalTo(1994));
	}

	/**
	 * Tears down the application after each test to preserve isolation.
	 */
	@AfterEach
	void tearDown() {
		seeder.closeConnection();
		app.stop();
	}

}
