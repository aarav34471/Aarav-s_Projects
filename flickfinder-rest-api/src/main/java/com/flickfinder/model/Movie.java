package com.flickfinder.model;

/**
 * Represents a movie with its unique identifier, title, and release year.
 */
public class Movie {

	private int id;
	private String title;
	private int year;

	/**
	 * Constructs a Movie object with the specified id, title, and year.
	 *
	 * @param id    the unique identifier of the movie
	 * @param title the title of the movie
	 * @param year  the release year of the movie
	 */
	public Movie(int id, String title, int year) {
		this.id = id;
		this.title = title;
		this.year = year;
	}

	/**
	 * Returns the unique identifier of the movie.
	 *
	 * @return the id of the movie
	 */
	public int getId() {
		return id;
	}

	/**
	 * Sets the unique identifier of the movie.
	 *
	 * @param id the id to set
	 */
	public void setId(int id) {
		this.id = id;
	}

	/**
	 * Returns the title of the movie.
	 *
	 * @return the title of the movie
	 */
	public String getTitle() {
		return title;
	}

	/**
	 * Sets the title of the movie.
	 *
	 * @param title the title to set
	 */
	public void setTitle(String title) {
		this.title = title;
	}

	/**
	 * Returns the release year of the movie.
	 *
	 * @return the release year of the movie
	 */
	public int getYear() {
		return year;
	}

	/**
	 * Sets the release year of the movie.
	 *
	 * @param year the release year to set
	 */
	public void setYear(int year) {
		this.year = year;
	}

	/**
	 * Returns a string representation of the Movie object.
	 * This is primarily used for debugging purposes.
	 *
	 * @return a string representation of the Movie object
	 */
	@Override
	public String toString() {
		return "Movie [id=" + id + ", title=" + title + ", year=" + year + "]";
	}

}