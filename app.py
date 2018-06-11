from flask import Flask, request
from flask_cors import CORS
import json
import kaplanmeier
import csv
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

client = MongoClient(host="localhost",port=27017)
db = client['test']
collection = db['naaccr']

@app.route('/')
def root():
    count = collection.find().count()
    data = {"case_count": count, "success": True}
    return json.dumps(data)

def state_to_fips(state):
    with open("statefips.csv",mode='r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if row['usps'] == state:
                return row['fips']

def get_dbfilter_from_request():
    dbfilter = request.values.get("dbfilter")
    if dbfilter is not None:
        dbfilter = json.loads(dbfilter)
    return dbfilter

def get_groupings_from_db(field_name, dbfilter = None):
    query = []
    if dbfilter is not None:
        query.append({'$match': dbfilter})
    query.append({'$group': {'_id': '$' + field_name, 'count': {'$sum': 1}}})
    result = collection.aggregate(query)
    return result

@app.route('/counts/',methods=['GET','POST'])
def get_counts():
    dbfilter = get_dbfilter_from_request()
    response = {}
    if dbfilter is not None:
        response['dbfilter'] = dbfilter
    response['data'] = []
    things_to_count = ['sex','primarySite','vitalStatus','ageAtDiagnosis','race1']
    for groupby in things_to_count:
        result = get_groupings_from_db(groupby, dbfilter)
        if groupby == 'ageAtDiagnosis':
            under18 = 0
            between18and65 = 0
            over65 = 0
            for row in result:
                if row['_id'] < 18:
                    under18 += 1
                elif row['_id'] >= 18 and row['_id'] < 65:
                    between18and65 += 1
                elif row['_id'] >= 65:
                    over65 += 1
            response['data'].append({groupby:'<18','count':under18})
            response['data'].append({groupby:'18-65','count':between18and65})
            response['data'].append({groupby:'>65','count':over65})
        else:
            for row in result:
                response['data'].append({groupby : row['_id'], 'count': row['count']})
        result.close()

    response['success'] = True
    return json.dumps(response)

@app.route('/charts/bar',methods=['GET','POST'])
def get_site_groupings():
    response = []
    dbfilter = get_dbfilter_from_request()
    result = get_groupings_from_db('primarySite',dbfilter)
    for row in result:
        response.append({'site':row['_id'], 'count':row['count']})
    return json.dumps(response)


@app.route('/charts/pie', methods=['GET', 'POST'])
def get_sex_counts():
    response = [0,0]
    dbfilter = get_dbfilter_from_request()
    result = get_groupings_from_db('sex',dbfilter)
    for row in result:
        if row['_id'] == "1":
            response[1] = row['count']
        if row['_id'] == "2":
            response[0] = row['count']
    return json.dumps(response)



@app.route('/charts/map',methods=['GET','POST'])
def get_geo_data():
    response = []
    dbfilter = get_dbfilter_from_request()
    result = get_groupings_from_db('addrAtDxState',dbfilter)
    for row in result:
        response.append({'state':row['_id'], 'count':row['count']})
    return json.dumps(response)


@app.route('/charts/map/<state>',methods=['GET', 'POST'])
def get_geo_data_by_state(state):
    response = []
    state = state.upper()

    dbfilter = get_dbfilter_from_request()
    if dbfilter is None:
        dbfilter = {"addrAtDxState": state}
    elif '$and' in dbfilter:
        dbfilter['$and'].append({"addrAtDxState": state})
    else:
        dbfilter = {'$and':[dbfilter,{"addrAtDxState": state}]}

    print(dbfilter)
    result = get_groupings_from_db('countyAtDx', dbfilter)
    for row in result:
        print(row)
        fips_county = str(state_to_fips(state)) + str(row['_id'])
        response.append({'county': fips_county, 'count':row['count']})
    return json.dumps(response)


@app.route('/charts/survival', methods=['GET', 'POST'])
def get_kaplan_meier_by_stage():
    response = {}
    response['treatments'] = []
    dbfilter = get_dbfilter_from_request()
    for stage in ['1','2','3','4']:
        if dbfilter is not None:
            stage_dbfilter = {'$and':[dbfilter, {"majorStageGrp":stage}]}
        else:
            stage_dbfilter = {"majorStageGrp":stage}
        result = collection.find(stage_dbfilter)
        km = kaplanmeier.kaplan_meier()
        count = 0
        for row in result:
            count += 1
            km.readFromJson(row)
        if count > 0:
            km.buildKaplanMeier(count)
            response['treatments'].append(km.buildJson())
        result.close()
    return json.dumps(response)


@app.route('/export/', methods=['GET', 'POST'])
def export_data_to_json():
    response = []
    dbfilter = get_dbfilter_from_request()
    result = collection.find(dbfilter)
    for row in result:
        del row['_id']
        response.append(row)
    return json.dumps(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
