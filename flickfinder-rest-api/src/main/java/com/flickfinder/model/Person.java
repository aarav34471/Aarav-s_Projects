package com.flickfinder.model;

/**
 * A person in the movie database.
 *
 * Represents a person in the movie database.
 */
public class Person {

	private int id;
	private String name;
	private int birth;
	public Person(int id, String name, int birth) {
		super();
		this.id = id;
		this.name = name;
		this.birth = birth;
	}
	public int getId() {
		return id;
	}
	public void setId(int id) {
		this.id = id;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public int getBirth() {
		return birth;
	}
	public void setBirth(int birth) {
		this.birth = birth;
	}

	public String toString() {
		return "Person [id=" + this.id + ", name=" + this.name + ", birth_year=" + this.birth + "]";
	}



}
