import os
import time
import datetime
import json
import traceback
import requests
import pymongo
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from concurrent.futures import wait
from concurrent.futures import ALL_COMPLETED

client = pymongo.MongoClient(host='localhost', port=27017)
db = client['stress_test']
task_col = db['tasks']
result_col = db['results']

# ---test url---
# url_new = "http://10.23.170.16:8964/api/v2/task/new"
# url_result = "http://10.23.170.16:8964/api/v2/result"

# ---Intranet url---
# url_new = "http://edge-diagnostic-live.bilibili.co/api/v2/task/new"
# url_result = "http://edge-diagnostic-live.bilibili.co/api/v2/result"

# ---Public network url---
url_new = "http://edge-diagnostic-live.bilivideo.com/api/v2/task/new"
url_result = "http://edge-diagnostic-live.bilivideo.com/api/v2/result"
headers = {'content-type': 'text/plain; charset=utf-8'}
payload = {'instance': {
    'ip': '125.121.107.71',
    'isp': '电信',
    'country': '中国',
    'province': '浙江',
    'city': '杭州',
    'latitude': '29.811436',
    'longitude': '119.672424',
    'provider': 'mcdn',
    'version': '1.0.7',
    'heartbeat': '2020-11-23T09:33:48.701000',
    'id': '5fbb5e1886d1b813f9bcbf63'
}
}


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        """
        检查bytes类型的数据转为str类型
        """
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)


class TaskManager(object):

    def __init__(self):
        self.object_id = ''
        self.task_id = ''
        self.result_dict = {}

    def create_task(self):
        data = json.dumps(payload, cls=MyEncoder, indent=4)
        # data = json.dumps(payload)
        try:
            res = requests.post(url=url_new, headers=headers, data=data, timeout=10)
            if res.status_code not in [200]:
                print('request /api/v2/task/new status_code : ', res.status_code)
                return ""
            res_data = res.json()["data"]
            add_res_data_mongodb = task_col.insert_one(res_data)
            self.object_id = add_res_data_mongodb.inserted_id
            self.task_id = res_data["task_id"]
        except Exception as e:
            print("error : ", e)
            traceback.print_exc()
        return self.task_id

    @staticmethod
    def get_secondary_domain(url):
        secondary_domain = url.split("//")[1].split(".")[0]
        return secondary_domain

    @staticmethod
    def get_target_cdn_str(url):
        target_cdn_str = url.split("|")[0]
        return target_cdn_str

    @staticmethod
    def get_suffix_str(url):
        suffix_str = url.split("|")[1]
        return suffix_str

    @staticmethod
    def get_trid_str(url):
        trid_str = url.split("&")[6].split("=")[1]
        return trid_str

    def handle_task(self):
        try:
            task = task_col.find_one({"task_id": self.task_id})
        except Exception as e:
            print("can not find task_id! --->", e)
            return
        self.result_dict["task_id"] = task["task_id"]
        self.result_dict["create_time"] = task["create_time"]
        self.result_dict["completed_time"] = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        self.result_dict["status"] = "Error"
        self.result_dict["data_sequence"] = "target_cdn_str|suffix_str|trid_str"
        data_list = []
        self.result_dict["data"] = data_list
        for url_task in task["urls"]:
            res_str = ""
            if url_task.split("|")[0] == "bvc":
                res_str = self.get_secondary_domain(url_task) + '|' + self.get_suffix_str(
                    url_task) + '|' + self.get_trid_str(url_task)
                data_list.append(res_str)
            else:
                res_str = self.get_target_cdn_str(url_task) + '|' + self.get_suffix_str(
                    url_task) + '|' + self.get_trid_str(url_task)
                data_list.append(res_str)
        if self.result_dict:
            self.result_dict["status"] = "Done"
        # result_col.insert_one(self.result_dict)
        return self.result_dict

    @staticmethod
    def callback_task(result_dict):
        data = json.dumps(result_dict)
        try:
            res = requests.post(url=url_result, data=data, timeout=10)
            if res.status_code not in [200, 202]:
                print('request /api/v2/result status_code : ', res.status_code)
                return ""
        except Exception as e:
            print("Callback task error! --->", e)
        return res


def get_create_task_qps():
    data = json.dumps(payload, cls=MyEncoder, indent=4)
    start_tick = datetime.datetime.now()
    i = 0
    while 1:
        i = i + 1
        try:
            requests.post(url=url_new, headers=headers, data=data, timeout=10)
        except Exception as e:
            print(e)
        end_tick = datetime.datetime.now()
        if (end_tick - start_tick).seconds == 1:
            break
    return i


def get_callback_task_qps():
    query_args = {}
    projection_fields = {'_id': False}
    result_dict = result_col.find_one(query_args, projection=projection_fields)
    data = json.dumps(result_dict, cls=MyEncoder, indent=4)
    start_tick = datetime.datetime.now()
    i = 0
    while 1:
        i = i + 1
        try:
            requests.post(url=url_result, data=data, timeout=10)
        except Exception as e:
            print(e)
        end_tick = datetime.datetime.now()
        if (end_tick - start_tick).seconds == 1:
            break
    return i


def task_create_task():
    tm = TaskManager()
    task_id = tm.create_task()
    if task_id:
        return 1
    else:
        print("create_task error!")
        return -1


def task_callback_task():
    query_args = {}
    projection_fields = {'_id': False}
    result_dict = result_col.find_one(query_args, projection=projection_fields)
    data = json.dumps(result_dict, cls=MyEncoder, indent=4)
    res = requests.post(url=url_result, data=data, timeout=10)
    if res.status_code in [200, 202]:
        return 1
    else:
        # print("callback_task error! ---> ", res.status_code)
        return -1


def task_one():
    tm = TaskManager()
    task_id = tm.create_task()
    # task_id = tm.task_id = '45eb650db78348f1ac28d6388c372ab0'
    if task_id:
        result_dict = tm.handle_task()
        if result_dict:
            print(result_dict)
            callback_res = tm.callback_task(result_dict)
            print("callback_res : ", callback_res)
            return 1
        else:
            print("handle_task error!")
            return -1
    else:
        print("create_task error!")
        return -1


def build_tasks_with_process(total_num, start_num):
    start_time = datetime.datetime.now()
    m_pool = Pool(total_num)
    for i in range(start_num):
        m_pool.apply_async(task_one(), args=(i,))
    m_pool.close()
    m_pool.join()
    end_time = datetime.datetime.now()
    execution_time = end_time - start_time
    print("execution_time : ", execution_time)


def build_tasks_with_thread(max_workers, start_num):
    success_num = 0
    start_time = datetime.datetime.now()
    executor = ThreadPoolExecutor(max_workers)
    all_task = [executor.submit(task_callback_task, ) for i in range(start_num)]
    # all_task = [executor.submit(task_create_task, ) for i in range(start_num)]
    # all_task = [executor.submit(task_one, ) for i in range(start_num)]
    for task_res in as_completed(all_task):
        if task_res.result() == 1:
            success_num = success_num + 1
        else:
            pass
    wait(all_task, return_when=ALL_COMPLETED)
    end_time = datetime.datetime.now()
    execution_time = end_time - start_time
    print("success_num : ", success_num)
    print("execution_time : ", execution_time)
    return success_num, execution_time


def main():
    # result = []
    # for i in range(5):
    #     res = build_tasks_with_thread(1000, 1000)
    #     time.sleep(5)
    #     result.append(res)
    # print(result)

    result = build_tasks_with_thread(100, 100)
    print(result)

    # build_tasks_with_process(500, 500)
    # print("/api/v2/task/new ---- qps :", get_create_task_qps())
    # print("/api/v2/result ---- qps :", get_callback_task_qps())


if __name__ == '__main__':
    main()
