import json
import requests
import os
from dotenv import load_dotenv
from CountryTable import CountryTable
from VisaStatusTable import VisaStatusTable
from CountryRequirementsTable import CountryRequirementsTable
from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.sql import text
from sqlalchemy_views import CreateView, DropView, metadata
from flask import Flask, send_from_directory, send_file, jsonify
import pandas as pd
import os

app = Flask(__name__)


def getCountryVisaRequirements(CountryDic):
    # return testdata.country_requirements_result_list
    countryRequirementsResultList = []
    for country in CountryDic:
        payLoad = {"citizenship": country}
        countryRequirementsResult = requests.get('https://visanotrequired.com/ein/visa-requirements', params=payLoad)
        countryRequirementsResultList.extend(countryRequirementsResult.json()["result"])
    return countryRequirementsResultList


def create_view_table(data_url):
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

    # print(str(create_view.compile()).strip())

    engine = create_engine(data_url)
    engine.execute(create_view)

    return create_view


@app.route("/create-tables")
def create_tables():
    load_dotenv()
    data_url = os.getenv('DATABASE_URL')
    metadata = MetaData()
    view = Table('country_visa', metadata)

    drop_view = DropView(view, cascade=True, if_exists=True)
    engine = create_engine(data_url)
    engine.execute(drop_view)

    ct = CountryTable(data_url)

    countryRequirementsResultList = getCountryVisaRequirements(ct.GetCountryDic())

    StatusTable = VisaStatusTable(data_url, countryRequirementsResultList)

    CountryRequirementsTable(data_url, countryRequirementsResultList, ct, StatusTable)
    create_view_table(data_url)
    return "okay"


@app.route("/csv")
def view_table_to_csv():
    load_dotenv()
    data_url = os.getenv('DATABASE_URL')
    conn = create_engine(data_url)
    df = pd.read_sql_query("SELECT * FROM country_visa", conn)

    directory_of_python_script = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(directory_of_python_script, "static/")

    filename = path + "data.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(df.to_csv())
    return send_file(filename, cache_timeout=0)


@app.route("/json")
def view_table_to_json():
    load_dotenv()
    data_url = os.getenv('DATABASE_URL')
    conn = create_engine(data_url)
    df = pd.read_sql_query("SELECT * FROM country_visa", conn)

    d = df.to_json(orient='records')
    print(type(d))
    json_object = json.loads(d)
    return jsonify(json_object)


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
