# Ratestask

## Project setup

I have developed this using basic python Flask framework. No ORM used to show use of SQL queries.
For running this locally, better to setup a virtual environment. For setting up virtual environment, refer the [extra details](#extra-details) section.

Install the dependencies using the below command:

```
pip install -r requirements.txt
```


## Running the project

Make sure the database is running before starting the application. 

```
python app.py
```

## Database setup

I used the given Docker setup, which starts a PostgreSQL instance populated with the assignment data.

Below are the same instructions given by you to setup the Database.

You can execute the provided Dockerfile by running:

```bash
docker build -t ratestask .
```

This will create a container with the name *ratestask*, which you can
start in the following way:

```bash
docker run -p 0.0.0.0:5432:5432 --name ratestask ratestask
```

You can connect to the exposed Postgres instance on the Docker host IP address,
usually *127.0.0.1* or *172.17.0.1*. It is started with the default user `postgres` and `ratestask` password.

```bash
PGPASSWORD=ratestask psql -h 127.0.0.1 -U postgres
```

alternatively, use `docker exec` if you do not have `psql` installed:

```bash
docker exec -e PGPASSWORD=ratestask -it ratestask psql -U postgres
```

Keep in mind that any data written in the Docker container will
disappear when it shuts down. The next time you run it, it will start
with a clean state.


## Extra details

Create a virtual environment using:

```
python -m venv env
```

Activate the virtual environment using:

```
source env/bin/activate
```