import requests
import pandas as pd
from sqlalchemy import create_engine
import testdata


class CountryTable:
    def __init__(self, data_url):
        self.countryDicList = []
        self.data_url = data_url
        self.countryDic = {}
        # self.countryDic=testdata.countryList
        self.demonymsDic = pd.read_csv('country_demonyms.csv', header=None, index_col=0, squeeze=True).to_dict()
        self.__initialize()

    # connects to psql database and adds countries data#
    def __initialize(self):
        """creates countries table in psql"""
        try:
            self.__setCountryData()
            engine = create_engine(self.data_url)
            dataframe = pd.DataFrame(self.countryDicList)
            dataframe.to_sql('countries', engine, if_exists='replace', index=False)
        except Exception as error:
            print('country table class initialization failed :' + str(error))

    # requests a countrylist when url is hit and returns a response that is converted to json#
    def __getCountryList(self):
        """returns a country list json response"""
        countryListResponse = requests.get('https://visanotrequired.com/ein/countrys')
        return countryListResponse.json()["result"]

    # sets countryData by converting countryList to countryDicList#
    def __setCountryData(self):
        countryList = self.__getCountryList()
        for index, country in enumerate(countryList):
            id = index + 1
            countrydic = {'name': country, 'id': id}
            self.countryDic[country] = id
            self.countryDicList.append(countrydic)

    def GetCountryDic(self):
        """returns countryDic"""
        return self.countryDic

    # Takes country checks if it exists in countrydic if it does it  convert the name  to id #
    def CountryNametoId(self, country):
        """converts country name to id returns none if it doesn't exist"""
        country = country.lower()
        if country in self.countryDic:
            return self.countryDic[country]
        else:
            return None

    # Takes demonyms checks if it exists in demonymsDic if it does it converts it to a an id#
    def DemonymsToCountry(self, demonyms):
        """converts demonyms to country returns none if it doesn't exist"""
        demonyms = demonyms.lower()
        if demonyms in self.demonymsDic:
            country = self.demonymsDic[demonyms]
            return self.CountryNametoId(country)
        else:
            return None
