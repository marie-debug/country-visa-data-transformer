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

    # connects to psql and adds data into database#
    def __initialize(self):
        """creates visa status table in psql"""
        try:
            self.__setCountryVisaData()
            dataframe = pd.DataFrame(self.visaDicList)
            engine = create_engine(self.data_url)
            dataframe.to_sql('visa_status', engine, if_exists='replace', index=False)
        except Exception as error:
            print('visa_status table class initialization failed :' + str(error))

    # converts countryRequirementsResultList into set#
    def __getCountryRequirementSet(self):
        countryRequirementSet = set()
        for countryRequirement in self.countryRequirementsResultList:
            # print(countryRequirement)
            countryRequirementSet.add(countryRequirement["Visa"].lower())
        return countryRequirementSet

    # sets visaStatusDic and visaDiclist#
    def __setCountryVisaData(self):
        countryRequirementSet = self.__getCountryRequirementSet()
        for index, visaStatus in enumerate(countryRequirementSet):
            id = index + 1
            visasdic = {'name': visaStatus, 'id': id}
            self.visaStatusDic[visaStatus] = id
            self.visaDicList.append(visasdic)

    def GetCountryVisaDic(self):
        """returns visaStatusDic"""
        return self.visaStatusDic

    def visaStatusToId(self, visaStatus):
        """Takes visaStatus checks if it exists in visaStatusDic if it doesn't it returns none"""
        visaStatus = visaStatus.lower()
        if visaStatus in self.visaStatusDic:
            return self.visaStatusDic[visaStatus]
        else:
            return None
