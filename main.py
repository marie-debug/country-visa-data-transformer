import requests
import os
from dotenv import load_dotenv
from CountryTable import CountryTable
from VisaStatusTable import VisaStatusTable
from CountryRequirementsTable import CountryRequirementsTable
from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.sql import text
from sqlalchemy_views import CreateView, DropView, metadata

load_dotenv()
data_url = os.getenv('DATABASE_URL')

ct = CountryTable(data_url)

CountryDic = ct.GetCountryDic()


def getCountryVisaRequirements(CountryDic):
    # return testdata.country_requirements_result_list
    countryRequirementsResultList = []
    for country in CountryDic:
        payLoad = {"citizenship": country}
        countryRequirementsResult = requests.get('https://visanotrequired.com/ein/visa-requirements', params=payLoad)
        countryRequirementsResultList.extend(countryRequirementsResult.json()["result"])
    return countryRequirementsResultList


countryRequirementsResultList = getCountryVisaRequirements(ct.GetCountryDic())

VisaStatusTable = VisaStatusTable(data_url, countryRequirementsResultList)

CountryRequirementsTable = CountryRequirementsTable(data_url, countryRequirementsResultList, ct, VisaStatusTable)


def create_view_table():
    metadata = MetaData()
    view = Table('country_visa', metadata)

    definition = text("""
                            SELECT visitor.name AS country_of_citizenship,
                            destination.name AS country_being_visited,
                            visa_status.name AS visa_requirements 
                            FROM countries_requirements
                            JOIN visa_status ON countries_requirements.visa_status=visa_status.id
                            JOIN countries AS destination
                            ON countries_requirements.destination_country=destination.id
                            JOIN countries AS visitor
                            ON countries_requirements.visitor_country=visitor.id
    """)

    create_view = CreateView(view, definition, or_replace=True)

    print(str(create_view.compile()).strip())

    engine = create_engine(data_url)
    engine.execute(create_view)


create_view_table()
