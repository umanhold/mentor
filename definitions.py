from dotenv import load_dotenv
import os

load_dotenv()

values = [os.environ['email'], os.environ['password']]
keys = ['_username','_password']
login_data = {k:v for (k,v) in zip(keys, values)} 

base = 'https://order.mentorium.de/admin/de'

SLEEP_INTERVAL_IN_S = 20
FACH = ['Statistik']
SOFTWARE = ['Stata']