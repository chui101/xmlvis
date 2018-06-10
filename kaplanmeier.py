import json
from datetime import datetime

jsonstring =[

    { "_id" : "5b1d4fd78e5651446c445449", "patientIdNumber" : 935, "dateOfDiagnosis" : 20110710, "addrAtDxState" : "AR", "derivedAjcc6StageGrp" : "99", "sex" : "2", "race1" : "99", "dateOfLastContact" : 20161104, "lengthOfFollowup" : 1944, "primarySite" : "C51", "ageAtDiagnosis" : 89, "derivedAjcc7StageGrp" : 999, "vitalStatus" : "1" },

    { "_id" : "5b1d4fd78e5651446c4454c7", "patientIdNumber" : 1061, "dateOfDiagnosis" : 20110318, "addrAtDxState" : "MO", "derivedAjcc6StageGrp" : "01", "lengthOfFollowup" : 0, "sex" : "1", "race1" : "99", "dateOfLastContact" : 20110318, "majorStageGrp" : "0", "primarySite" : "C67", "ageAtDiagnosis" : 50, "derivedAjcc7StageGrp" : 10, "vitalStatus" : "1" },

    { "_id" : "5b1d4fd78e5651446c4455ce", "patientIdNumber" : 1324, "dateOfDiagnosis" : 20120130, "addrAtDxState" : "TX", "derivedAjcc6StageGrp" : "01", "lengthOfFollowup" : 0, "sex" : "1", "race1" : "96", "dateOfLastContact" : 20120130, "majorStageGrp" : "0", "primarySite" : "C67", "ageAtDiagnosis" : 72, "derivedAjcc7StageGrp" : 10, "vitalStatus" : "1" },

    { "_id" : "5b1d4fd88e5651446c445634", "patientIdNumber" : 1426, "dateOfDiagnosis" : 20100306, "addrAtDxState" : "NY", "derivedAjcc6StageGrp" : "01", "lengthOfFollowup" : 0, "sex" : "2", "race1" : "99", "dateOfLastContact" : 20100306, "majorStageGrp" : "0", "primarySite" : "C67", "ageAtDiagnosis" : 70, "derivedAjcc7StageGrp" : 10, "vitalStatus" : "1" }
]



class kaplanMeier:

    def __init__(self):
        self.kmc = []

    def buildJson(self):
        jsonbody= []
        i=0
        while i<len(self.kmc):

            test = {
                "t": self.kmc[i][0],
                "d": self.kmc[i][1],
                "n": self.kmc[i][2]

            }
            jsonbody.append(test)
            i+=1
        return jsonbody


    # reading from a single JSON
    def readFromJson(self,Json):

        data = json.loads(json.dumps(Json))

        vitalstatus = data["vitalStatus"]
        # calculate number of days
        dateOfDiagnosis = datetime.strptime(str(data["dateOfDiagnosis"]), '%Y%m%d')
        dateOfLastContact = datetime.strptime(str(data["dateOfLastContact"]), '%Y%m%d')

        t = dateOfLastContact-dateOfDiagnosis

        # performing linear search everytime
        if(len(self.kmc)==0):
            if (vitalstatus == 0):
                self.kmc.append([t.days , 1, 0])
            else:
                self.kmc.append([t.days, 0, -1])


        else:
            i = 0
            while i < len(self.kmc):
                if (self.kmc[i][0] == t.days):
                    if (vitalstatus == 0):
                        self.kmc[i][1] += 1
                    else:
                        self.kmc[i][2] -= 1

                    break
                i+=1

            if (i==len(self.kmc)):
                if (vitalstatus == 0):
                    self.kmc.append([t.days, 1, 0])
                else:
                    self.kmc.append([t.days, 0, -1])

        """
        #sample data
        self.kmc.append([1, 2, 0])
        self.kmc.append([20, 0, 0])
        self.kmc.append([8, 1, -1])
        self.kmc.append([400, 0, 0])
        self.kmc.append([974, 1, 0])
        self.kmc.append([874, 0, -1])
        """
        return self.kmc


    def buildKaplanMeier(self, totalpopulation):
        self.kmc.sort()



        self.kmc[0][2] = totalpopulation - self.kmc[0][1] + self.kmc[0][2]
        #print(0, " ", self.kmc[0][0], "-", self.kmc[0][1], "-", self.kmc[0][2])
        i = 1
        while i < len(self.kmc):
            self.kmc[i][2] = self.kmc[i - 1][2] - self.kmc[i][1] + self.kmc[i][2]
            #if self.kmc[i][1] > 0:
             #   print(i, " ", self.kmc[i][0], "-", self.kmc[i][1], "-", self.kmc[i][2])
            i = i + 1

        return self.kmc






km=kaplanMeier()
a = []
i=0
while i<len(jsonstring):
    a+=km.readFromJson(jsonstring[i])
    i+=1

km.buildKaplanMeier(len(jsonstring))
print(km.buildJson())