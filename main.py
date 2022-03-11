import requests
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from CountryTable import CountryTable
from VisaStatusTable import VisaStatusTable
import json
import testdata
import warnings

load_dotenv()
data_url = os.getenv('DATABASE_URL')

ct = CountryTable(data_url)

CountryDic = ct.GetCountryDic()


def getCountryVisaRequirements(CountryDic):
    # return testdata.countryRequirementsResultList
    countryRequirementsResultList = []
    for country in CountryDic:
        payLoad = {"citizenship": country}
        countryRequirementsResult = requests.get('https://visanotrequired.com/ein/visa-requirements', params=payLoad)
        countryRequirementsResultList.extend(countryRequirementsResult.json()["result"])
    return countryRequirementsResultList


countryRequirementsResultList = getCountryVisaRequirements(ct.GetCountryDic())

VisaStatusTable = VisaStatusTable(data_url, countryRequirementsResultList)

requirementDicList = []

for requirement in countryRequirementsResultList:

    destinationCountry = ct.CountryNametoId(requirement['Name'])
    if destinationCountry is None:
        warnings.warn("Warning: country not found in country list {}".format(requirement['Name'].lower()))
        continue

    visitorCountry = ct.DemonymsToCountry(requirement['Citizen'])
    if visitorCountry is None:
        warnings.warn("Warning: demonym not found in demonymsDic {}".format(requirement['Citizen'].lower()))
        continue

    visaStatus = VisaStatusTable.visaStatusToId(requirement['Visa'])
    if visaStatus is None:
        warnings.warn("Warning: visaStatus not found in visaDic {}".format(requirement['Visa'].lower()))
        continue

    requirementDic = {
        'destinationCountry': destinationCountry,
        'visitorCountry': visitorCountry,
        'visaStatus': visaStatus
    }
    requirementDicList.append(requirementDic)

requirementDataframe = pd.DataFrame(requirementDicList)

engine = create_engine(data_url)

requirementDataframe.to_sql('countriesRequirements', engine, if_exists='replace', index=False)
