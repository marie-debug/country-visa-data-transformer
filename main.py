import requests
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from CountryTable import CountryTable
import json

load_dotenv()
data_url = os.getenv('DATABASE_URL')

ct = CountryTable(data_url)

countryList = ct.GetCountryList()

print(countryList)
