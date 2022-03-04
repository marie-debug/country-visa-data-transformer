import requests
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from CountryTable import CountryTable
from VisaStatusTable import VisaStatusTable
import json

load_dotenv()
data_url = os.getenv('DATABASE_URL')

ct = CountryTable(data_url)

countryList = ct.GetCountryList()

print(countryList)


def getCountryVisaRequirements(countryList):
    countryRequirementsResultList = []
    for country in countryList:
        payLoad = {"citizenship": country}
        countryRequirementsResult = requests.get('https://visanotrequired.com/ein/visa-requirements', params=payLoad)
        countryRequirementsResultList.extend(countryRequirementsResult.json()["result"])
    return countryRequirementsResultList


countryRequirementsResultList = getCountryVisaRequirements(countryList)

VisaStatusTable(data_url, countryRequirementsResultList)
