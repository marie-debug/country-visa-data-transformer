import requests
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


def getCountryList():
    countryListResponse = requests.get('https://visanotrequired.com/ein/countrys')
    countryList = countryListResponse.json()["result"]
    return countryList


def getCountryDataFrame(countryList):
    countryDicList = []
    for index, country in enumerate(countryList):
        countrydic = {'name': country, 'id': index + 1}
        countryDicList.append(countrydic)
    countryDataFrame = pd.DataFrame(countryDicList)
    return countryDataFrame


countryList = getCountryList()
countryDataFrame = getCountryDataFrame(countryList)

data_url = os.getenv('DATABASE_URL')
engine = create_engine(data_url)

countryDataFrame.to_sql('countries', engine, if_exists='replace', index=False)

'''countryRequirementsResultList = []
for country in countryList:
    payLoad = {"citizenship": country}
    countryRequirementsResult = requests.get('https://visanotrequired.com/ein/visa-requirements', params=payLoad)
    countryRequirementsResult.json()
    countryRequirementsResultList.extend(countryRequirementsResult.json()["result"])

df = pd.json_normalize(countryRequirementsResultList)
print(df)'''
