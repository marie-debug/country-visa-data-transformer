from sqlalchemy import create_engine
import pandas as pd


class VisaStatusTable:
    def __init__(self, data_url, countryRequirementsResultList):
        self.data_url = data_url
        self.countryRequirementsResultList = countryRequirementsResultList
        self.__initialize()

    def __initialize(self):
        try:
            dataframe = self.__getCountryVisaDataFrame()
            engine = create_engine(self.data_url)
            dataframe.to_sql('visaStatus', engine, if_exists='replace', index=False)
        except Exception as error:
            print('visaStatus table class initialization failed :' + str(error))

    def __getCountryRequirementSet(self):
        countryRequirementSet = set()
        for countryRequirement in self.countryRequirementsResultList:
            # print(countryRequirement)
            countryRequirementSet.add(countryRequirement["Visa"].lower())
        return countryRequirementSet

    def __getCountryVisaDataFrame(self):
        visaDicList = []
        countryRequirementSet = self.__getCountryRequirementSet()
        for index, visas in enumerate(countryRequirementSet):
            visasdic = {'name': visas, 'id': index + 1}
            visaDicList.append(visasdic)
            # print(visaDicList)
        dataframe = pd.DataFrame(visaDicList)
        return dataframe
