from sqlalchemy import create_engine
import pandas as pd
import testdata


class VisaStatusTable:
    def __init__(self, data_url, countryRequirementsResultList):
        self.data_url = data_url
        self.countryRequirementsResultList = countryRequirementsResultList
        self.visaDicList = []
        self.visaStatusDic = {}
        # self.visaStatusDic=testdata.visaStatusDic
        self.__initialize()

    def __initialize(self):
        try:
            self.__setCountryVisaData()
            dataframe = pd.DataFrame(self.visaDicList)
            engine = create_engine(self.data_url)
            dataframe.to_sql('visa_status', engine, if_exists='replace', index=False)
        except Exception as error:
            print('visa_status table class initialization failed :' + str(error))

    def __getCountryRequirementSet(self):
        countryRequirementSet = set()
        for countryRequirement in self.countryRequirementsResultList:
            # print(countryRequirement)
            countryRequirementSet.add(countryRequirement["Visa"].lower())
        return countryRequirementSet

    def __setCountryVisaData(self):
        countryRequirementSet = self.__getCountryRequirementSet()
        for index, visaStatus in enumerate(countryRequirementSet):
            id = index + 1
            visasdic = {'name': visaStatus, 'id': id}
            self.visaStatusDic[visaStatus] = id
            self.visaDicList.append(visasdic)

    def GetCountryVisaDic(self):
        return self.visaStatusDic

    def visaStatusToId(self, visaStatus):
        visaStatus = visaStatus.lower()
        if visaStatus in self.visaStatusDic:
            return self.visaStatusDic[visaStatus]
        else:
            return None
