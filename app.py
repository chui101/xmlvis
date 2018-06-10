from flask import Flask, request
import json
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient(host="localhost",port=27017)
db = client['test']
collection = db['naaccr']

@app.route('/')
def root():
    count = collection.find().count()
    data = {"case_count": count, "success": True}
    return json.dumps(data)

@app.route('/counts/')
def getcounts():
    filter = request.args.get("filter")
    response = {}
    if filter != None:
        filter = json.loads(filter)
        response['filter'] = filter
    response['data'] = []
    things_to_count = ['sex','primarySite','vitalStatus','ageAtDiagnosis','race1']
    for groupby in things_to_count:
        query = []
        if filter != None:
            query.append({'$match': filter})
        query.append({'$group': {'_id':'$'+ groupby, 'count':{'$sum':1} } })
        result = collection.aggregate(query)
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

@app.route('/charts/bar')
def getsitegroupings():
    response = []
    query = []
    filter = request.args.get("filter")
    if filter != None:
        filter = json.loads(filter)
        query.append({'$match': filter})

    query.append({'$group': {'_id': '$primarySite', 'count': {'$sum': 1}}})
    result = collection.aggregate(query)
    for row in result:
        response.append({'site':row['_id'], 'count':row['count']})
    return json.dumps(response)

if __name__ == '__main__':
    app.run()
