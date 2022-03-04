import requests
import pandas as pd
from sqlalchemy import create_engine


class CountryTable:
    def __init__(self, data_url):
        self.countryList = None
        self.data_url = data_url
        self.__initialize()

    def __initialize(self):
        try:
            self.__setCountryList()
            dataframe=self.__getCountryDataFrame()
            engine = create_engine(self.data_url)
            dataframe.to_sql('countries', engine, if_exists='replace', index=False)
        except Exception as error:
            print('country table class initialization failed :' + str(error))

    def __setCountryList(self):
        countryListResponse = requests.get('https://visanotrequired.com/ein/countrys')
        self.countryList = countryListResponse.json()["result"]

    def __getCountryDataFrame(self):
        countryDicList = []
        for index, country in enumerate(self.countryList):
            countrydic = {'name': country, 'id': index + 1}
            countryDicList.append(countrydic)
        dataframe = pd.DataFrame(countryDicList)
        return dataframe


    def GetCountryList(self):
        return self.countryList
