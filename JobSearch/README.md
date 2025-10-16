Welcome to your repo for COM2027, Group 16!
=====================================================

Feel free to change this README.

Getting started
---------------

Before you get started, you should update your com2027.yml file with your team members and project details. This will appear at [your static site](https://csee.pages.surrey.ac.uk/com2027/2024-25/Group16).

You have two branches created for you, `trunk` and `release`. The final commit on `release` will be marked.

Commits must be merged into `release` using a merge request, which requires two approvals. Force-pushing is disabled for both branches, as this can destroy your work. Only `trunk` can be merged into `release`.

You may develop directly on `trunk`, although it is recommended that you branch from `trunk` and submit merge requests (or merge directly onto the branch). How you use `trunk` is up to your team.

## Backend Requirements

### Linux

1. Install PostgreSQL and pre-requisites:
    ```sh
    sudo apt-get update
    sudo apt-get install postgresql postgresql-contrib
    sudo apt-get install libpq-dev python3-dev
    ```

    
### Windows or macOS

1. Download and install PostgreSQL from the [official website](https://www.postgresql.org/download/).

### Setting up PostgreSQL dataase
For detailed instructions on setting up PostgreSQL with Django, refer to [this guide](https://djangocentral.com/using-postgresql-with-django/).

### Additional PostgreSQL command
When you set up the database run the following:
1. Setting Database owner:
   ```sh
    sudo systemctl start postgresql
    sudo -u postgres psql
    ALTER DATABASE mydb OWNER TO myuser;
    \q

    ```


### Additional Requirements
If you are running on your local machine

1. Install additional Python requirements:
    ```sh
    cd backend
    python -m venv venv
    pip install -r requirements.txt
    ```

## Frontend Requirements

1. Install Node Package Manager (NPM) for your system from the [official website](https://nodejs.org/en/download).

2. In the frontend directory, run the following commands:
    ```sh
    cd frontend
    npm install
    npm install @react-google-maps/api
    npm run build
    npm run start
    ```


## Building with Docker

It is recommended to stop any local instances of PostgreSQL before building with Docker. To build with docker run the commands in the root of the folder


1. If you encounter an error that port 5432 is not accepting connections, run the following command to stop the local PostgreSQL service:
    ```sh
    sudo systemctl stop postgresql
    ```
    
2. Build and start the Docker containers:
    ```sh
    docker compose up --build 
    ```

    or 

    ```sh
    docker-compose up --build
    ```
    
3. Stop and remove containers:
    ```sh
    docker-compose down    
    ```
    or

    ```sh
    docker compose down
    ```