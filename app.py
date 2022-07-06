import grequests
import json
from CountryTable import CountryTable
from VisaStatusTable import VisaStatusTable
from CountryRequirementsTable import CountryRequirementsTable
from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.sql import text
from sqlalchemy_views import CreateView, DropView, metadata
from flask import Flask, send_file, jsonify
import pandas as pd
import os


app = Flask(__name__)


def generateUrls(CountryDic):
    urls = []
    for country in CountryDic:
        url = 'https://visanotrequired.com/ein/visa-requirements?citizenship={}'.format(country)
        urls.append(url)
    return urls


def getCountryVisaRequirements(urls):
    reqs = [grequests.get(link) for link in urls]
    resp = grequests.map(reqs)
    return resp




def create_view_table(data_url):
    """Takes data_url, creates and returns a view table """
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


def getdatabaseUrl():
    # heroku generates a database url with 'postgres'
    # sqlalchemy requires the database url to start with 'postgresql'
    data_url = os.getenv('DATABASE_URL')
    return data_url.replace("postgres://", "postgresql://", 1)


# creates table in psql when url is hit#

@app.route("/create-tables")
def create_tables():
    """creates tables in psql """
    data_url = getdatabaseUrl()
    metadata = MetaData()
    view = Table('country_visa', metadata)

    drop_view = DropView(view, cascade=True, if_exists=True)
    engine = create_engine(data_url)
    engine.execute(drop_view)

    ct = CountryTable(data_url)
    urls = generateUrls(ct.GetCountryDic())
    responses = getCountryVisaRequirements(urls)

    countryRequirementsResultList = []
    for response in responses:
        countryRequirementsResultList.extend(response.json()["result"])

    StatusTable = VisaStatusTable(data_url, countryRequirementsResultList)

    CountryRequirementsTable(data_url, countryRequirementsResultList, ct, StatusTable)
    create_view_table(data_url)
    return "okay"


# converts view table to csv when url is hit and stores it to static#

@app.route("/csv")
def view_table_to_csv():
    """converts view table to csv """

    data_url = getdatabaseUrl()
    conn = create_engine(data_url)
    df = pd.read_sql_query("SELECT * FROM country_visa", conn)

    directory_of_python_script = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(directory_of_python_script, "static/")

    filename = path + "data.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(df.to_csv())
    return send_file(filename, cache_timeout=0)


# converts view table to json when url is hit#
@app.route("/json")
def view_table_to_json():
    """converts view table to json """

    data_url = getdatabaseUrl()
    conn = create_engine(data_url)
    df = pd.read_sql_query("SELECT * FROM country_visa", conn)

    d = df.to_json(orient='records')
    print(type(d))
    json_object = json.loads(d)
    return jsonify(json_object)


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
