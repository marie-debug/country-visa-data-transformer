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

countryRequirementSet = set()
for countryRequirement in countryRequirementsResultList:
    # print(countryRequirement)
    countryRequirementSet.add(countryRequirement["Visa"].lower())

#print(countryRequirementSet)

engine = create_engine(data_url)


def visadataframe(set):
    visaDicList = []
    for index, visas in enumerate(set):
        visasdic = {'name': visas, 'id': index + 1}
        visaDicList.append(visasdic)
        #print(visaDicList)
    return pd.DataFrame(visaDicList)


visa=visadataframe(countryRequirementSet)

visa.to_sql('visas', engine, if_exists='replace', index=False)
