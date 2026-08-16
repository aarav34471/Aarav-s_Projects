# FlickFinder REST API

FlickFinder is a layered Java REST API for querying movies, people, and starring relationships from a SQLite database.

## Architecture

```mermaid
flowchart LR
    Client --> Routes[Javalin routes]
    Routes --> Controllers[Movie and person controllers]
    Controllers --> DAOs[JDBC data-access objects]
    DAOs --> DB[(SQLite movie database)]
```

- **Routes** map HTTP resources to controller methods.
- **Controllers** validate request parameters, translate missing records into HTTP responses, and serialise models as JSON.
- **DAOs** use JDBC prepared statements to query movies, people, and relationship tables.
- **Models** provide serialisable movie and person representations.

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/movies/` | List movies; accepts an optional `limit` query parameter. |
| `GET` | `/movies/{id}` | Retrieve one movie. |
| `GET` | `/movies/{id}/stars` | List people starring in a movie. |
| `GET` | `/people/` | List people; accepts an optional `limit` query parameter. |
| `GET` | `/people/{id}` | Retrieve one person. |
| `GET` | `/people/{id}/movies` | List movies associated with a person. |

## Running the API

Requirements: Java 17 and Maven.

```bash
mvn clean test
mvn package
```

The database is not committed. During Maven's `generate-resources` phase, the configured download plugin retrieves the read-only development database and writes it to `src/main/resources/movies.db`. Run `com.flickfinder.Main` from an IDE or Maven-compatible launcher after the build, then access the API on port `9000`.

## Testing

The test suite uses JUnit 5, Mockito, REST Assured, and an in-memory seeded database. It covers models, DAOs, controllers, and end-to-end routes without requiring the full development database.

## Limitations

- The API is read-only and has no authentication or pagination metadata.
- Some related-record queries execute one query per relationship and could be replaced with joins.
- Input parsing should return explicit `400` responses for invalid numeric parameters.
