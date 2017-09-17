# -*-  coding:utf-8  -*-
'''
探索数据
'''
from pymongo import MongoClient
import pprint

def get_pipeline(key):
	if key == "building":
		return  [
		{"$match": {"building": {"$exists": 1}}},
		{"$group": {"_id": "$building",
					"count": {"$sum": 1}}},
		{"$sort": {"count": -1}},
		{"$limit": 12}
		]
	if key == "church":
		return [
		{"$match": {"building": {"$in":["church", "cathedral"]}}},
		{"$group": {"_id": "$name"}},
		{"$limit": 15}
		]
	if key == "craft": #统计手工作坊类型排名
		return [
		{"$match": {"craft": {"$exists": 1}}},
		{"$group": {"_id": "$craft",
					"count": {"$sum": 1}}},
		{"$sort": {"count": -1}},
		{"$limit": 10}

		]
	if key == "user": #统计总的用户数目
		return [
		{"$match": {"created.user": {"$exists": 1}}},
		{"$group": {"_id": "$created.user",
					"count": {"$sum": 1}}},
		{"$group": {"_id": "Total user number",
					"total user number": {"$sum": 1}}}	
		]
	return None

def get_db(db_name):
	client = MongoClient("localhost:27017")
	db = client[db_name]
	return db

def aggregate(db, pipeline):
	return [doc for doc in db.osm.aggregate(pipeline)]

def iter_print(result):
	for doc in result:
		pprint.pprint(doc)

if __name__ == "__main__":
	db = get_db("adelaide")
	pipeline = get_pipeline("user")
	result = aggregate(db, pipeline)
	#query = get_query("")
	#result = db.osm.find(query)
	#print db.osm.find({"building": {"$in": [None, "yes"]}}).count()
	iter_print(result)

