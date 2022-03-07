import requests
import pandas as pd
from sqlalchemy import create_engine


class CountryTable:
    def __init__(self, data_url):
        self.countryDicList = []
        self.data_url = data_url
        self.countryDic = {}
        self.__initialize()

    def __initialize(self):
        try:
            self.__setCountryData()
            engine = create_engine(self.data_url)
            dataframe = pd.DataFrame(self.countryDicList)
            dataframe.to_sql('countries', engine, if_exists='replace', index=False)
        except Exception as error:
            print('country table class initialization failed :' + str(error))

    def __getCountryList(self):
        countryListResponse = requests.get('https://visanotrequired.com/ein/countrys')
        return countryListResponse.json()["result"]

    def __setCountryData(self):
        countryList = self.__getCountryList()
        for index, country in enumerate(countryList):
            id=index + 1
            countrydic = {'name': country, 'id':id}
            self.countryDic[country] = id
            self.countryDicList.append(countrydic)

    def GetCountryDic(self):
        return self.countryDic
