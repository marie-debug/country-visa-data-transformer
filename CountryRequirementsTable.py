from sqlalchemy import create_engine
import warnings
import pandas as pd


class CountryRequirementsTable:
    def __init__(self, data_url, country_requirements_result_list, country_table, visa_status_table):
        self.data_url = data_url
        self.requirementDicList = []
        self.country_requirements_result_list = country_requirements_result_list
        self.country_table = country_table
        self.visa_status_table = visa_status_table
        self.__initialize()

    def __initialize(self):
        try:
            self.__setCountryRequirementsData()
            requirementDataframe = pd.DataFrame(self.requirementDicList)
            engine = create_engine(self.data_url)
            requirementDataframe.to_sql('countries_requirements', engine, if_exists='replace', index=False)
        except Exception as error:
            print('countries_requirements table class initialization failed :' + str(error))

    def __setCountryRequirementsData(self):
        for requirement in self.country_requirements_result_list:
            destinationCountry = self.country_table.CountryNametoId(requirement['Name'])
            if destinationCountry is None:
                warnings.warn("Warning: country not found in country list {}".format(requirement['Name'].lower()))
                continue

            visitorCountry = self.country_table.DemonymsToCountry(requirement['Citizen'])
            if visitorCountry is None:
                warnings.warn("Warning: demonym not found in demonymsDic {}".format(requirement['Citizen'].lower()))
                continue

            visaStatus = self.visa_status_table.visaStatusToId(requirement['Visa'])
            if visaStatus is None:
                warnings.warn("Warning: visaStatus not found in visaDic {}".format(requirement['Visa'].lower()))
                continue

            requirementDic = {
                'destination_country': destinationCountry,
                'visitor_country': visitorCountry,
                'visa_status': visaStatus
            }
            self.requirementDicList.append(requirementDic)
