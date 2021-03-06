# libaries
import requests
import time
import datetime
from bs4 import BeautifulSoup
import bs4
import os
import re
from definitions import *


def login():
	''' log in to plattform '''
	s = requests.Session()
	url = f'{base}/login'
	try:
		r = s.get(url)
		soup = BeautifulSoup(r.content, 'html5lib')
		login_data['_csrf_token'] = soup.find('input', attrs={'name': '_csrf_token'})['value']
		s.post(url, data=login_data)
		return s

	except requests.exceptions.SSLError as e:
		print(e)

def list2str(strlist):
	string = ''
	for e in strlist:
		string = string + e.replace('  ','')
	return string

def parse_project(s, match):
	''' parse project 
	0 bestellnr
	1 service
	2 Fach
	3 klasse
	4 ue
	5 sprache
	6 umsetzungsdauer
	7 fachbereich
	8 software
	9 umfrage tool
	10 wurde die umfrage bereits...
	11 grund
	12 themen
	13 bei der auswertung dabei sein...
	14 prüfungsdatum
	15 umsetzungszeitraum
	'''
	oid = match.text.strip()
	url = f'{base}/freelancer/requested_course_orders/{oid}/show'

	try:
		r = s.get(url)
		trs = BeautifulSoup(r.content, 'html5lib').findAll('tr', {'class': 'sonata-ba-view-container'})

		project = [trs[i].text for i in range(0,16)]
		keys = [item.strip().split('\n')[0] for item in project]
		values = []
		for item in project:
			value = list2str(item.strip().split('\n')[1:])
			if value == '':
				value = 'Keine Angabe'
			values.append(value)
			
		d = {k:v for (k,v) in zip(keys, values)}

		return d, oid, s

	except requests.exceptions.SSLError as e:
		return None, None, s
		print(e)


def parse_project_list(s):
	''' parse project list '''
	rlist = [None, None, s]
	try:
		r = s.get(f'{base}/freelancer/requested_course_orders/list')
		soup = BeautifulSoup(r.content, 'html5lib')
		info_box = soup.find('span', {'class': 'info-box-text'})
		match = soup.find('td', {'class': 'sonata-ba-list-field sonata-ba-list-field-integer'})
		if info_box is None and match is not None:
			return parse_project(s, match)
		else:
			return rlist

	except requests.exceptions.SSLError as e:
		print(e)
		return rlist

	except Exception as e:
		print(e)
		return rlist

def loop():
	''' check for new projects every SLEEP_INTERVAL_IN_S seconds '''

	d_pre = {}
	s = login()
	while True:
		try:
			d, oid, s = parse_project_list(s)
			if d != None and d != d_pre:

				
				project_description = (
					"\n\n"
					+"Service: "+d["Service"]+"\n"
					+"Fach: "+d["Fach"]+"\n"
					+"Unterrichtseinheiten: "+d["Unterrichtseinheiten"]+"\n"
					+"Sprache: "+d["Sprache"]+"\n"
					+"Umsetzungsdauer: "+d["Umsetzungsdauer"]+"\n"
					+"Fachbereich: "+d["Fachbereich"]+"\n"
					+"Software: "+d["Software"]+"\n"
					+"Umsetzungszeitraum: "+d["Umsetzungszeitraum"]+"\n\n"
				)

				print(project_description)

				if 'Datenanalyse' not in d['Service'] and 'Datenanalyse' not in d['Fach']:
					try:
						r = s.get(f'{base}/freelancer/requested_course_orders/{oid}/denyRequest')
					except Exception as e:
						print(e)
				elif 'Stata' in d['Software']:
					try:
						r = s.get(f'{base}/freelancer/requested_course_orders/{oid}/acceptRequest')
					except Exception as e:
						print(e)
				else:
					d_pre = d
			else:
				pass
		except Exception as e:
			print(e)
		time.sleep(SLEEP_INTERVAL_IN_S)  