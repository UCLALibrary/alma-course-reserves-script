# alma-course-reserves-script
A python script to generate a list of active Alma course reserves for integration with campus systems.

Requires Python 3 (tested with Python 3.7.3) and the 3rd-party `requests`module (installed via `requirements.txt`, below).

## Initial setup

1. Clone the repository.

		$ git clone https://github.com/UCLALibrary/alma-course-reserves-script.git

2. Use the repo.

		$ cd alma-course-reserves-script

3. Create virtual environment.

		$ python3 -m venv ENV
		$ source ENV/bin/activate

4. Update pip and install the Python packages

		$ pip install --upgrade pip
		$ pip install -r requirements.txt

5. Place the separately-provided `alma_api_keys.py` file in the `alma-course-reserves-script` directory.

## Running the script
		
		$ cd /path/to/alma-course-reserves-script
		$ source ENV/bin/activate
		$ ./get_course_reserves.py

The script will create (or replace) a file called `course_reserves_data.csv` in the current directory.
This is a CSV file with a headings row, which lists 4 columns:

* code: The course code, like `ANTHRO 129`
* name: The course name, like `Selected Topics in Biological Anthropology: Forensic Anthropology`
* section: The course/section id, which should be a 9-digit string like `111477300`
* url: A URL which does a search for the given `section` in UCLA's UC Library Search

The script may print some messages, if there are any active course reserves in Alma with invalid data:

* No section (course lacks section id)
* Invalid section (section id is present but is not a 9-digit string)
* Invalid end date (end date is more than a year in the future, suggesting data problems)

The output file will not have rows for these courses with invalid data.
