# BLT HR Portal

## Dependencies

**Language:** Python3

**Libraries:** `pip install -r requirements.txt`

## Usage

1. Clone this repo
2. Using the command line, navigate to the root of this project
3. Run `python manage.py runserver`

### Database Changes

From the root of this project run the following commmands

1. `python manage.py makemigrations blt_hr_system` (generates the migrations)
2. `python manage.py migrate` (applies migrations to the database)
3. Load inital data: `python manage.py loaddata access_levels.json`

If you need to reset migrations (locally)

1. Remove the all migrations files within `blt_hr_system/migrations` except for `__init__.py`
2. Drop the project database
	- `psql` (enter PostgreSQL)
	- `DROP DATABASE blt_hr_system;` (drop the database)
	- `\q` (to quit)
3. Create the project database
	- `psql`
	- `CREATE DATABASE blt_hr_system;` (create the database)
	- `\l` (list all the databases to ensure it was created)
4.  Add `system-admin` as an account
	- `python manage.py createsuperuser`
	- Username: `system_admin`

### Database Changes on the deployment

1. Reset all data in the database: `heroku pg:reset DATABASE -a blt-construction`
2. Run migrations `heroku run python manage.py makemigrations -a blt-construction`
3. `heroku run python manage.py migrate -a blt-construction`
4. `heroku run python manage.py createsuperuser -a blt-construction`