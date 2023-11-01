from datetime import date
import sys
import requests

url = 'http://192.168.1.221:5000/checkbackup'
user_agent = {'User-agent': '438IF96YW'}


resp = requests.post(url, headers = user_agent) 
sys.exit()