import pymongo
import time
import datetime
import json
import requests

# client = pymongo.MongoClient(host='localhost', port=27017)
# db = client['stress_test']
# task_col = db['tasks']
#
# # res = task_col.insert_one({"lilie": 10})
# # print(res.inserted_id)
#
# res = task_col.find_one({'status': 'alive'})
# print(res)
#
# res = task_col.find_one({'msg': 'success.'})['data']
# print(res)
# # task_col.insert_one(res)
#
#
# res = task_col.find_one({'task_id': '93041fd6eb2c4351b2b0ac62ff298b77'})
# print(res)


startTick = datetime.datetime.now()
i = 0
while 1:
    i = i + 1
    endTick = datetime.datetime.now()
    if (endTick - startTick).seconds >= 1:
        break

print(i)


url_new = "http://edge-diagnostic-live.bilibili.co/api/v2/task/new"
url_result = "http://edge-diagnostic-live.bilibili.co/api/v2/result"
headers = {'content-type': 'text/plain; charset=utf-8'}
payload = {"instance": {
    "ip": "114.233.54.174",
    "isp": "电信",
    "country": "中国",
    "province": "江苏",
    "city": "泰州",
    "latitude": "33.831573",
    "longitude": "115.75856",
    "provider": "mcdn",
    "version": "1.0.7",
    "heartbeat": "2020-10-27T10:19:48.295000",
    "id": "5f916833f9f34f50059ba1cb",
    "group_id": "5f571e85ab4fefab65b1ecb2"
}
}

# payload = {'instance': {
#     'ip': '114.233.54.174',
#     'isp': '电信',
#     'country': '中国',
#     'province': '江苏',
#     'city': '泰州',
#     'latitude': '33.831573',
#     'longitude': '115.75856',
#     'provider': 'mcdn',
#     'version': '1.0.7',
#     'heartbeat': '2020-10-27T10:19:48.295000',
#     'id': '5f916833f9f34f50059ba1cb',
#     'group_id': '5f571e85ab4fefab65b1ecb2'
# }
# }


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)


# data = json.dumps(payload, cls=MyEncoder, indent=4)
# # data = json.dumps(payload)
# try:
#     res = requests.post(url=url_new, headers=headers, data=data, timeout=10)
#     res_data = res.json()["data"]
#     print(res_data)
# except Exception as e:
#     print("error : ", e)


lt = [[1, 2, 3], {'name': 'xiaoming'}]  # 创建一个lt列表
encoded_json = json.dumps(lt)  # 将lt列表，进行json格式化编码
lt_str = repr(lt)  # 把lt转化为字符串
print("type lt_str : ", type(lt_str))  # str
print("type encoded_json : ", type(encoded_json))  # str
decode_json = json.loads(encoded_json)
print("type decode_json : ", type(decode_json))  # list
print(decode_json)

dt = {'name1': 'xiaoming', 'name2': 'xiaozhang', 'name3': 'xiaoliu'}  # 创建一个dt字典
encoded_json = json.dumps(dt)  # 将lt列表，进行json格式化编码
print("type dt : ", type(dt))  # dict
print("type encoded_json : ", type(encoded_json))  # str
decode_json = json.loads(encoded_json)
print("type decode_json : ", type(decode_json))  # dict
print(decode_json)



