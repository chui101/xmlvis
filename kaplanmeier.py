class KaplanMeier:

    def __init__(self):
        self.km_counts = {}
        self.population = 0

    def to_timepoints(self):
        result= []
        for time in sorted(self.km_counts):
            row = {
                "t": time,
                "d": self.km_counts[time][0],
                "n": self.km_counts[time][1]

            }
            result.append(row)
        return result


    # reading from a single JSON
    def add_record(self,json):
        self.population += 1
        vital_status = json["vitalStatus"]
        follow_up_length = json['lengthOfFollowup']
        if follow_up_length < 0:
            follow_up_length = 0

        if follow_up_length not in self.km_counts:
            self.km_counts[follow_up_length] = [0,0]

        if vital_status == 0:
            self.km_counts[follow_up_length][0] += 1
        else:
            self.km_counts[follow_up_length][1] -= 1

    def calculate(self):
        time_points = sorted(self.km_counts)
        for i in range(len(time_points)):
            # start calculating final numbers with the final population count
            if i == 0:
                time = time_points[i]
                self.km_counts[time][1] = self.population - self.km_counts[time][0] + self.km_counts[time][1]
            # calculate each subsequent time point using the remaining population from the previous time point
            else:
                time = time_points[i]
                prev_time = time_points[i-1]
                self.km_counts[time][1] = self.km_counts[prev_time][1] - self.km_counts[time][0] + self.km_counts[time][1]




if __name__ == "__main__":
    jsonstring =[
        { "_id" : "5b1d4fd78e5651446c445449", "patientIdNumber" : 935, "dateOfDiagnosis" : 20110710, "addrAtDxState" : "AR", "derivedAjcc6StageGrp" : "99", "sex" : "2", "race1" : "99", "dateOfLastContact" : 20161104, "lengthOfFollowup" : 1944, "primarySite" : "C51", "ageAtDiagnosis" : 89, "derivedAjcc7StageGrp" : 999, "vitalStatus" : "1" },
        { "_id" : "5b1d4fd78e5651446c4454c7", "patientIdNumber" : 1061, "dateOfDiagnosis" : 20110318, "addrAtDxState" : "MO", "derivedAjcc6StageGrp" : "01", "lengthOfFollowup" : 0, "sex" : "1", "race1" : "99", "dateOfLastContact" : 20110318, "majorStageGrp" : "0", "primarySite" : "C67", "ageAtDiagnosis" : 50, "derivedAjcc7StageGrp" : 10, "vitalStatus" : "1" },
        { "_id" : "5b1d4fd78e5651446c4455ce", "patientIdNumber" : 1324, "dateOfDiagnosis" : 20120130, "addrAtDxState" : "TX", "derivedAjcc6StageGrp" : "01", "lengthOfFollowup" : 0, "sex" : "1", "race1" : "96", "dateOfLastContact" : 20120130, "majorStageGrp" : "0", "primarySite" : "C67", "ageAtDiagnosis" : 72, "derivedAjcc7StageGrp" : 10, "vitalStatus" : "1" },
        { "_id" : "5b1d4fd88e5651446c445634", "patientIdNumber" : 1426, "dateOfDiagnosis" : 20100306, "addrAtDxState" : "NY", "derivedAjcc6StageGrp" : "01", "lengthOfFollowup" : 0, "sex" : "2", "race1" : "99", "dateOfLastContact" : 20100306, "majorStageGrp" : "0", "primarySite" : "C67", "ageAtDiagnosis" : 70, "derivedAjcc7StageGrp" : 10, "vitalStatus" : "1" }
    ]
    km=KaplanMeier()
    a = []
    for record in jsonstring:
        a+=km.readFromJson(record)
    km.buildKaplanMeier(len(jsonstring))
    print(km.buildJson())