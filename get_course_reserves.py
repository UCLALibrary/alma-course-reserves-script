#!/usr/bin/env python3
"""
Retrieves Alma course reserves data via API,
and outputs relevant data as tab-delimited file.
"""
import csv
import json
import re
import requests
from datetime import datetime, timedelta, timezone
# UCLA-specific API key management
from alma_api_keys import API_KEYS

BASE_URL = 'https://api-na.hosted.exlibrisgroup.com'
# UCLA-specific API key
API_KEY = API_KEYS['CAMPUS_COURSES']
HEADERS = {'Authorization': f'apikey {API_KEY}',
           'Accept': 'application/json',
           'Content-Type': 'application/json'}

def call_get_api(api, parameters):
	get_url = BASE_URL + api + parameters
	response = requests.get(get_url, headers=HEADERS)
	if (response.status_code != 200):
		#TODO: Real error handling
		print(response.status_code)
		print(response.headers)
		print(response.text)
	return response

def get_primo_url(section):
	# Returns the UCLA Primo URL which searches specifically for section 
	return f'https://search.library.ucla.edu/discovery/search?query=course_code,contains,{section},AND&tab=CourseReserves&search_scope=CourseReserves&vid=01UCS_LAL:UCLA&lang=en&mode=advanced&offset=0'

def get_current_data():
	api = '/almaws/v1/courses/'
	course_list = []
	# Unknown number of results available until first batch is retrieved.
	# Request 100 at a time, starting at the beginning.
	limit = 100
	offset = 0	# Covers 1-limit (or total results, if less than limit)
	current_count = -1
	total_count = 0
	while current_count < total_count:
		parameters = f'?status=ACTIVE&limit={limit}&offset={offset}'
		response = call_get_api(api, parameters)
		course_data = json.loads(response.text)
		# course_data is a dictionary with 'course' (a list of dictionaries), and 'total_record_count'
		total_count = course_data['total_record_count']
		for course in course_data['course']:
			# start_date and end_date only for data review, not final output
			course_dict = {
				'code': course['code'].strip(),
				'name': course['name'].strip(),
				'section': course['section'].strip(),
				'start_date': course['start_date'],
				'end_date': course['end_date'],
			}
			if course_dict['section'] != '':
				course_dict['url'] = get_primo_url(course_dict['section'])
			# Don't add bad data
			if _course_data_is_good(course_dict):
				# Remove keys not needed for output
				course_dict.pop('start_date')
				course_dict.pop('end_date')
				# And add what's left to the list of courses
				course_list.append(course_dict)
		offset += limit
		current_count += limit
	return course_list

def _course_data_is_good(course_data):
	# Checks data for current course for validity
	valid = True
	section = course_data['section']
	# API returns dates like '2021-10-05Z'; UTC is fine here
	end_date = datetime.strptime(course_data['end_date'], '%Y-%m-%d%z')
	# One year from now, also in UTC
	future = datetime.now(timezone.utc) + timedelta(365)
	if section == '':
		valid = False
		validation_message = 'No section: '
	elif re.search('^[0-9]{9}$', section) is None:
		valid = False
		validation_message = f'Invalid section {section}: '
	elif end_date > future:
		valid = False
		validation_message = f'Invalid end date {end_date}: '
	if valid == False:
		print(validation_message + f"{course_data['code']} / {course_data['name']}")
	return valid

def main():
	course_list = get_current_data()
	keys = course_list[0].keys()
	with open('course_reserves_data.csv', 'w') as f:
		writer = csv.DictWriter(f, keys)
		writer.writeheader()
		writer.writerows(course_list)

if __name__ == '__main__':
	main()
