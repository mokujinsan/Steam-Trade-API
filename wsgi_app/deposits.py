from bson.objectid import ObjectId
import json


class DatabaseDeposits():
    def __init__(self, db):
        self.collection = db["deposits"]

    def get(self, deposit_id):
        return self.collection.find_one({"_id": ObjectId(deposit_id)}, {"_id": 0})

    def get_processing(self):
        return list(self.collection.find({"status": {"$lt": 3}}, {"_id": 0}))

    def get_steam_id(self, steam_id, active=True):
        if active:
            return list(self.collection.find({"steam_id": steam_id, "status": {"$lt": 3}}, {"_id": 0}))
        return list(self.collection.find({"steam_id": steam_id, "status": {"$gte": 3}}, {"_id": 0}))

    def add(self, server_id, steam_id, trade_token, assets, report_url, security_code, celery_task_id, bot, additional):
        new_deposit = {
            "server_id": server_id,
            "steam_id": steam_id,
            "trade_token": trade_token,
            "assets": json.dumps(assets),
            "report_url": report_url,
            "security_code": security_code,
            "bot": bot,
            "data": json.dumps(additional),
            "celery_task_id": celery_task_id,
            "message": None,
            "status": 0
        }
        result = self.collection.insert(new_deposit)
        return result is not None

    def set_data(self, steam_id, key, value):
        last_deposit = list(self.collection.find({"steam_id": steam_id}).limit(1).sort("_id", -1))[0]
        last_data = json.loads(last_deposit["data"])
        last_data[key] = value
        result = self.collection.update({"_id": last_deposit["_id"]}, {"$set": {"data": json.dumps(last_data)}})
        return result['ok'] == 1

    def change_status_last(self, steam_id, status):
        last_deposit = list(self.collection.find({"steam_id": steam_id}).limit(1).sort("_id", -1))[0]
        result = self.collection.update({"_id": last_deposit["_id"]}, {"$set": {"status": int(status)}})
        return result['ok'] == 1

    def change_celery_task_id_last(self, steam_id, celery_task_id):
        last_deposit = list(self.collection.find({"steam_id": steam_id}).limit(1).sort("_id", -1))[0]
        result = self.collection.update({"_id": last_deposit["_id"]}, {"$set": {"celery_task_id": celery_task_id}})
        return result['ok'] == 1

    def change_message_last(self, steam_id, message):
        last_deposit = list(self.collection.find({"steam_id": steam_id}).limit(1).sort("_id", -1))[0]
        result = self.collection.update({"_id": last_deposit["_id"]}, {"$set": {"message": message}})
        return result['ok'] == 1