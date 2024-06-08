## COM1028 Software Engineering - FlickFinder

This is the starting project for the COM1028 Software Engineering module. This project is a simple application that provides a RESTful API for accessing a movie database. The database is a simple SQLite database that contains information about movies, people, and their relationships.

## Dependencies

Overall, we have the following dependencies in our project:

- [sqllite-jdbc](https://mvnrepository.com/artifact/org.xerial/sqlite-jdbc) - SQLite JDBC Driver
- [javalin](https://javalin.io/) - A simple web framework for Java
- [junit](https://junit.org/junit5/) - JUnit for unit testing
- [mockito](https://site.mockito.org/) - Mockito for mocking objects in unit tests
- [rest-assured](https://rest-assured.io/) - Testing and validating our APIs

These dependencies are managed by Maven, and you can find them in the [pom.xml](pom.xml) file.

## Database

### Development Database

The database is a simple SQLite database that contains information about movies, people, and their relationships. The database is structured as follows:

![Database](https://csee.pages.surrey.ac.uk/com1028/res/ERD.png)

You've been given the IMDB movies database to work with. It is a simple database and you will only need to interact with it in a read only manner; you will not be adding data or modifying the database.

You can find the database in the [src/main/resources](src/main/resources) folder. The database is called `movies.db`. You should not modify this database in any way. However, it won't be there until you run the project for the first time. I am using the com.googlecode.maven-download-plugin to pull the database in from a remote location. This is defined in the [pom.xml](pom.xml) file. It should be pulled when you run the project for the first time.

### Testing Database

Although the development database is simple, it has a lot of data. This can make testing difficult. For testing we use a in-memory database. This database is created and populated with data before each test and destroyed after each test. This code can be found in [src/test/java/com/flickfinder/util/Seeder.java](src/test/java/com/flickfinder/util/Seeder.java).

## Getting Started

1. Clone the repository: `git clone <repository address>`
2. Open the project in your favourite IDE (IntelliJ, Eclipse, etc.). While you can use any IDE, these instructions will assume you are using Eclipse. The project is a Maven project; as such, the process should be similar in other IDEs.
3. In Eclipse, got to File -> Open Projects from File System... and select the root directory of the project.

![Open Project](https://csee.pages.surrey.ac.uk/com1028/res/open_project.png)

4. In the package explorer, right click on the project and select Run As -> Maven Install. This will download all the dependencies and build the project, including the database.

![Maven Install](https://csee.pages.surrey.ac.uk/com1028/res/maven_install.png)

5. If all has gone well, you should see a message in the console saying "BUILD SUCCESS". If you see this, you are ready to run the project. Ignore, any warnings or errors about JRE System Library.

![Build Success](https://csee.pages.surrey.ac.uk/com1028/res/build_success.png)

6. To run the project, right click on the project in the package explorer and locate `src/main/java/com/flickfinder/Main.java`, right click on this file and select Run As -> Java Application.

7. You'll see a warning in the console: "SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder". This is not a problem and can be ignored.

8. Open a browser. Ideally one with JSON rendering capabilities (e.g.Firefox or Chrome with a JSON extension). In the address bar, type `http://localhost:8000`. If all has gone well, you should see the API documentation.
