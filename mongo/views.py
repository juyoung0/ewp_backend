from django.shortcuts import render
from pymongo import MongoClient
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from mongo.sample import sample, stored
from mongo.simulsample import sample2, stored2
from mongo.sample2 import corr5, corr6, corr7, corr8
from mongo.sample3 import stop_history, stop_keys, stop_dates, machine_structure
from django.http import HttpResponse
from datetime import time as dttime
from datetime import datetime, date, timedelta
import json
import math
import collections
import logging, logging.handlers
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import threading, time
from django.middleware.gzip import GZipMiddleware
import io, gzip
from multiprocessing import Process
#GZIP 인코딩
gzip_middleware = GZipMiddleware()

# 로거 인스턴스를 만든다
logger = logging.getLogger('mylogger')
# 포매터를 만든다
fomatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
# 스트림과 파일로 로그를 출력하는 핸들러를 각각 만든다.
#fileHandler = logging.FileHandler('/home/juyoungoh/LoggerTest.log')
fileHandler = logging.FileHandler('LoggerTest.log')
streamHandler = logging.StreamHandler()
# 각 핸들러에 포매터를 지정한다.
fileHandler.setFormatter(fomatter)
streamHandler.setFormatter(fomatter)
# 로거 인스턴스에 스트림 핸들러와 파일핸들러를 붙인다.
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)
logging.basicConfig(level=logging.DEBUG)


import mongo.KEWP_utils as utils

# Create your views here.
TAG_LIST = {} #dictionary

class mongoAPI(APIView):
    #permission_classes = (IsAuthenticated,)

    @api_view(['GET'])
    def return_structure(request):
        json_result = json.dumps(col_obj.data_obj.structure, ensure_ascii=False)
        return HttpResponse(json_result, content_type='application/json; charset=utf-8')

    @csrf_exempt
    @api_view(['POST'])
    def return_stophistory(request):
        result = {"history":stop_history, "dates":stop_dates}
        if request.method == 'POST':
            params = request.body.decode("utf8")
            params = json.loads(params)
            logging.info("Parameter : " + str(params))
            t = params['tag']
            if t[5]=='5' or t[6]=='5': #5호기 SHOULD 따른 호끼 추까하끼
                stop_tag_list = col_obj.data_obj.tagHistoryList(t, 5)
            elif t[5]=='6' or t[6]=='6': #5호기 SHOULD 따른 호끼 추까하끼
                stop_tag_list = col_obj.data_obj.tagHistoryList(t, 6)
            elif t[5]=='7' or t[6]=='7': #5호기 SHOULD 따른 호끼 추까하끼
                stop_tag_list = col_obj.data_obj.tagHistoryList(t, 7)
            elif t[5]=='8' or t[6]=='8': #5호기 SHOULD 따른 호끼 추까하끼
                stop_tag_list = col_obj.data_obj.tagHistoryList(t, 8)
            result = stop_tag_list

        json_result = json.dumps(result, ensure_ascii=False)
        return HttpResponse(json_result, content_type='application/json; charset=utf-8')

    @csrf_exempt
    @api_view(['POST'])
    def return_correlation(request):
        json_result = ""
        if request.method == 'POST':
            params = request.body.decode("utf8")
            params = json.loads(params)
            logging.info("Parameter : " + str(params))
            m = params['machine']
            if m=="5":
                json_result = json.dumps(corr5, ensure_ascii=False)
            elif m=="6":
                json_result = json.dumps(corr6, ensure_ascii=False)
            elif m=="7":
                json_result = json.dumps(corr7, ensure_ascii=False)
            elif m=="8":
                json_result = json.dumps(corr8, ensure_ascii=False)

        return HttpResponse(json_result, content_type='application/json; charset=utf-8')

    @csrf_exempt
    @api_view(['POST'])
    def simulation_json(request):
        if request.method == 'POST':
            params = request.body.decode("utf8")
            params = json.loads(params)
            logging.info("Parameter : " + str(params))
            s = params['start']
            e = params['end']
            f = "%Y-%m-%dT%H:%M:%S.%fZ"
            s_parse = datetime.strptime(s, f)
            e_parse = datetime.strptime(e, f)
            col_obj.simul_obj.simulation['start'] = s_parse
            col_obj.simul_obj.simulation['end'] = e_parse
            col_obj.simul_obj.simulation['interval'] = timedelta(seconds=60*int(params['interval'])) #최소 데이터베이스 간격이 1분이라면, interval=5분 일때, interval=5
            #Calculate start index, interval (index)
            year = int(s_parse.strftime('%Y'))
            month = int(s_parse.strftime('%m'))
            day = int(s_parse.strftime('%d'))
            year2 = int(e_parse.strftime('%Y'))
            month2 = int(e_parse.strftime('%m'))
            day2 = int(e_parse.strftime('%d'))

            col_obj.simul_obj.idx = datetime(year, month, day, 0, 0, 0)
            col_obj.simul_obj.endidx = datetime(year2, month2, day2, 0, 0, 0)
            d = date(year, month, day)
            t = dttime(0, 0, 0)

            col_obj.simul_obj.idx = datetime(year, month, day, 0, 0, 0)
            col_obj.simul_obj.endidx = datetime(year2, month2, day2, 0, 0, 0)

            #first load history data for one day
            col_obj.loadSimulationHistoryData()
            col_obj.loadSimulationJsonData()
            result = col_obj.simul_obj.getTempData()
        else :
            col_obj.simul_obj.idx += col_obj.simul_obj.simulation['interval']
            if col_obj.simul_obj.idx == col_obj.simul_obj.endidx:
                result = {}
            else:
                col_obj.loadSimulationJsonData()
                result = col_obj.simul_obj.getTempData()

        json_result = json.dumps(result, ensure_ascii=False)

        return HttpResponse(json_result, content_type='application/json; charset=utf-8')

    @csrf_exempt
    @api_view(['POST'])
    def simulation(request):
        if request.method == 'POST':
            params = request.body.decode("utf8")
            params = json.loads(params)
            logging.info("Parameter : " + str(params))
            s = params['start']
            e = params['end']
            f = "%Y-%m-%dT%H:%M:%S.%fZ"
            s_parse = datetime.strptime(s, f)
            e_parse = datetime.strptime(e, f)
            col_obj.simul_obj.simulation['start'] = s_parse
            col_obj.simul_obj.simulation['end'] = e_parse
            #Calculate start index, interval (index)
            year = int(s_parse.strftime('%Y'))
            month = int(s_parse.strftime('%m'))
            day = int(s_parse.strftime('%d'))
            year2 = int(e_parse.strftime('%Y'))
            month2 = int(e_parse.strftime('%m'))
            day2 = int(e_parse.strftime('%d'))

            col_obj.simul_obj.idx = datetime(year, month, day, 0, 0, 0)
            col_obj.simul_obj.endidx = datetime(year2, month2, day2, 0, 0, 0)

            col_obj.loadSimulationListData()

        result = col_obj.data_obj.getSimulationListData()
        json_result = json.dumps(result, ensure_ascii=False, sort_keys=True)
        return HttpResponse(json_result, content_type='application/json; charset=utf-8')

    @csrf_exempt
    @api_view(['POST'])
    #Get Law data of one tag (connect to one collection)
    def connect_mongo_tag(request):
        result = []

        if request.method == 'POST':
            params = request.body.decode("utf8")
            params = json.loads(params)
            logging.info("Parameter : " + str(params))
            s = params['date']
            f = "%Y-%m-%dT%H:%M:%S.%fZ"
            date_parse = datetime.strptime(s, f)
            t_name = params['tag']
           # dd = date(int(params['year']), int(params['month']), int(params['day']))
           # tt = dttime(int(params['hour']), int(params['minute']), int(params['second']))
            dd = date(int(date_parse.strftime('%Y')), int(date_parse.strftime('%m')), int(date_parse.strftime('%d')))
            tt = dttime(int(date_parse.strftime('%H')), int(date_parse.strftime('%M')), int(date_parse.strftime('%S')))
            dt = datetime.combine(dd, tt)
            cursor = col_obj.find2(t_name, dt)

            for c in cursor:
                result.append(c)

        json_result = json.dumps(result, ensure_ascii=False)

        return HttpResponse(json_result, content_type='application/json; charset=utf-8')

    #Get specific date data (specific period) for ALL tag
    @csrf_exempt
    @api_view(['POST'])
    def connect_mongo_all(request):
        result = col_obj.data_obj.getSearchedDataAll()

        if request.method == 'POST':
            params = request.body.decode("utf8")
            params = json.loads(params)
            logging.info("Parameter : " + str(params))
            s = params['date']
            f = "%Y-%m-%dT%H:%M:%S.%fZ"
            date_parse = datetime.strptime(s, f)
            s2 = params['date2']
            date_parse2 = datetime.strptime(s2, f)
            dd = date(int(date_parse.strftime('%Y')), int(date_parse.strftime('%m')), int(date_parse.strftime('%d')))
            tt = dttime(int(date_parse.strftime('%H')), int(date_parse.strftime('%M')), int(date_parse.strftime('%S')))
            dt = datetime.combine(dd, tt)
            dd2 = date(int(date_parse2.strftime('%Y')), int(date_parse2.strftime('%m')), int(date_parse2.strftime('%d')))
            tt2 = dttime(int(date_parse2.strftime('%H')), int(date_parse2.strftime('%M')), int(date_parse2.strftime('%S')))
            dt2 = datetime.combine(dd2, tt2)

            # if col_obj.data_obj.idx == 0: #first load from requested date
            col_obj.searchDateAll(dt, dt2)

            # col_obj.dict_to_json()
            result = col_obj.data_obj.getSearchedDataAll()

        json_result = json.dumps(result, ensure_ascii=False)

        return HttpResponse(json_result, content_type='application/json')

    @csrf_exempt
    @api_view(['GET'])
    def connect_mongo_json(request):
        # Update
        result = {}
        if request.method == 'GET':
           # machine = request.GET.get('n') #나중에 호기별 디비 생기면, 따로 연결하도록 하기
            #if len(col_obj.data_obj.tempData['children']) == 0:
            #    col_obj.InitloadJsonData() #initiate tree sturcture first
            #else:
                #col_obj.loadJsonData()
            result = col_obj.data_obj.getTempData()
        zbuf = io.BytesIO()
        zfile = gzip.GzipFile(mode='w', compresslevel=6, fileobj=zbuf)
        json_str = json.dumps(result, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')
        zfile.write(json_bytes)
        zfile.close()
        compressed_content = zbuf.getvalue()
        response = HttpResponse(compressed_content)
        response['Content-Length'] = str(len(response.content))
        response['Content-Encoding'] = 'gzip'
        return response
        # json_result = json.dumps(result, ensure_ascii=False)
        # return HttpResponse(json_result, content_type='application/json; charset=utf-8')

    @csrf_exempt
    @api_view(['GET'])
    def connect_mongo_list_data(request):
        result = col_obj.data_obj.getListData()

        zbuf = io.BytesIO()
        zfile = gzip.GzipFile(mode='w', compresslevel=6, fileobj=zbuf)
        json_str = json.dumps(result, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')
        zfile.write(json_bytes)
        zfile.close()
        compressed_content = zbuf.getvalue()
        response = HttpResponse(compressed_content)
        response['Content-Length'] = str(len(response.content))
        response['Content-Encoding'] = 'gzip'
        return response
        #return gzip_middleware.process_response(request, response)
        #return HttpResponse(json_result, content_type='application/json; charset=utf-8')

    #Get specific date data (specific period) for one tag
    @csrf_exempt
    @api_view(['POST'])
    def connect_mongo_data(request):
        result = []
        predict = []
        if request.method == 'POST':
            params = request.body.decode("utf8")
            params = json.loads(params)
            logging.info("Parameter : " + str(params))
            s = params['date']
            f = "%Y-%m-%dT%H:%M:%S.%fZ"
            date_parse = datetime.strptime(s, f)
            s2 = params['date2']
            date_parse2 = datetime.strptime(s2, f)
            dd = date(int(date_parse.strftime('%Y')), int(date_parse.strftime('%m')), int(date_parse.strftime('%d')))
            tt = dttime(int(date_parse.strftime('%H')), int(date_parse.strftime('%M')), int(date_parse.strftime('%S')))
            dd2 = date(int(date_parse2.strftime('%Y')), int(date_parse2.strftime('%m')), int(date_parse2.strftime('%d')))
            tt2 = dttime(int(date_parse2.strftime('%H')), int(date_parse2.strftime('%M')), int(date_parse2.strftime('%S')))
            dt = datetime.combine(dd, tt)
            dt2 = datetime.combine(dd2, tt2)
            t_name = params['tag']  # request.POST.get('tag')

            cursor = col_obj.find3(t_name, dt, dt2)
            for c in cursor:
                result.append({'val':c['val'], 'Date':c['Date'], 'predict':c['prediction'], 'prob':c['prob']})

        zbuf = io.BytesIO()
        zfile = gzip.GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
        json_str = json.dumps(result, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')
        zfile.write(json_bytes)
        zfile.close()
        compressed_content = zbuf.getvalue()
        response = HttpResponse(compressed_content)
        response['Content-Length'] = str(len(response.content))
        response['Content-Encoding'] = 'gzip'
        return response
        # json_result = json.dumps(result, ensure_ascii=False)
        # return HttpResponse(json_result, content_type='application/json')

    @csrf_exempt
    @api_view(['POST'])
    def connect_mongo_history(request):
        #col_obj.data_obj.sortHistoryTag()

        if request.method == 'POST':
            params = request.body.decode("utf8")
            params = json.loads(params)
            logging.info("Parameter : " + str(params))
            # if params['isSimulation']=="True":
            #     result = col_obj.simul_obj.getHistoryData()
            # else:
            result = col_obj.data_obj.getHistoryData()
        else:
            result = col_obj.data_obj.getHistoryData()

        json_result = json.dumps(result, ensure_ascii=False)

        return HttpResponse(json_result, content_type='application/json')

    @csrf_exempt
    @api_view(['POST'])
    def connect_mongo_power(request):
        result = col_obj.data_obj.getPowerData()
        r = []
        if request.method == 'POST':
            params = request.body.decode("utf8")
            params = json.loads(params)
            logging.info("Parameter : " + str(params))
            s = params['date']
            f = "%Y-%m-%dT%H:%M:%S.%fZ"
            date_parse = datetime.strptime(s, f)
            s2 = params['date2']
            date_parse2 = datetime.strptime(s2, f)
            dd = date(int(date_parse.strftime('%Y')), int(date_parse.strftime('%m')), int(date_parse.strftime('%d')))
            tt = dttime(int(date_parse.strftime('%H')), int(date_parse.strftime('%M')), int(date_parse.strftime('%S')))
            dt = datetime.combine(dd, tt)
            dd2 = date(int(date_parse2.strftime('%Y')), int(date_parse2.strftime('%m')), int(date_parse2.strftime('%d')))
            tt2 = dttime(int(date_parse2.strftime('%H')), int(date_parse2.strftime('%M')), int(date_parse2.strftime('%S')))
            dt2 = datetime.combine(dd2, tt2)

            cursor = col_obj.power_collection.find({"Date" : {'$gte': str(dt),'$lt' : str(dt2)}})

            for c in cursor:
               r.append(c)

            result = r
            col_obj.data_obj.setPowerData(result)

        json_result = json.dumps(result, ensure_ascii=False)

        #return render(request, 'showPOWER.html', {'result': json_result})
        return HttpResponse(json_result, content_type='application/json')

    @csrf_exempt
    @api_view(['POST'])
    def connect_mongo_important(request):
        if request.method == 'POST':
            params = request.body.decode("utf8")
            params = json.loads(params)
            logging.info("Parameter : " + str(params))
            # if params['isSimulation']=="True":
            #     result = col_obj.simul_obj.getImportantData()
            # else:
            result = col_obj.data_obj.getImportantData()
        else:
            result = col_obj.data_obj.getImportantData()
        zbuf = io.BytesIO()
        zfile = gzip.GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
        json_str = json.dumps(result, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')
        # zfile.write(json_bytes)
        # zfile.close()
        # content = zbuf.getvalue()
        # zbuf.seek(0,0)
        # content = zbuf.read()
        content = gzip.compress(json_bytes)
        print(content)
        response = HttpResponse(content)
        response['Content-Length'] = str(len(response.content))
        response['Content-Encoding'] = 'gzip'
        print(response)
        return response
        # json_result = json.dumps(result, ensure_ascii=False)
        # return HttpResponse(json_result, content_type='application/json')

    @csrf_exempt
    @api_view(['POST'])
    def connect_mongo_change_th(request):
        if request.method == 'POST':
            params = request.body.decode("utf8")
            params = json.loads(params)
            logging.info("Parameter : " + str(params))
            # if params['isSimulation']=="True":
            #     col_obj.simul_obj.importantThreshold = params['threshold']
            # else:
            col_obj.data_obj.importantThreshold = params['threshold']

    @csrf_exempt
    @api_view(['POST'])
    #Get specific date data (specific period) for one tag
    def connect_mongo_stop(request):
        result = {}
        if request.method == 'POST':
            params = request.body.decode("utf8")
            params = json.loads(params)
            logging.info("Parameter : " + str(params))
            s = params['date']
            f = "%Y-%m-%d"
            date_parse = datetime.strptime(s, f)
            day = date_parse.strftime('%Y')+date_parse.strftime('%m')+date_parse.strftime('%d')
            cursor = col_obj.stop_collection[day].find({})

            result['name'] = cursor[0]['name']
            result['children'] = cursor[0]['children']

        json_result = json.dumps(result, ensure_ascii=False)
        return HttpResponse(json_result, content_type='application/json')


class DataHub(object):
    def __init__(self):
       # self.tempData = sample
        self.tempData = {"name": "EWP", "children": []}
        self.structure = {"structure":machine_structure}
        self.listData = {"plant":{"1":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[],"9":[],"10":[]}}
        self.historyData = stored
        self.searchedDataAll = stored
        self.powerData = {}
        self.searchedData = {}
        self.tagImportantList = []
        self.idx = datetime(2015, 1, 1, 0, 0, 0)
        self.idx_step = timedelta(seconds=60)
        self.importantData = {'columns':['호기','계통','설비','name','r','v','dt'],'tags':{}}
        self.importantThreshold = 0.3
        #self.historyInit = False
        self.s_initialized = {"1":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[],"9":[],"10":[]} #호기별 태그의 초기화 상태
        self.h_initialized = {"1":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[],"9":[],"10":[]} #호기별 태그의 초기화 상태

        logging.info("Datahub is initated")

    #store the latest data to history data & remove the oldest data
    def store1(self, df):
        self.historyData['dt'] = df['dt']
        form = {"data":{"name":df['name'],"호기":df['호기']},"val":df['r']}
        self.tagImportantList.append(form)

        if df['name'] in self.h_initialized[df['호기']]:
            # store the latest data to history data
            old_data = self.historyData['machines'][df['호기']][df['name']]
            old_data.append(df)
            # remove the oldest data from history data
            new_time = datetime.strptime(df['dt'], '%Y-%m-%d %H:%M:%S')
            old_time = new_time - timedelta(days=1)
            new_data = [item for item in old_data if item['dt'] > str(old_time)]
            self.historyData['machines'][df['호기']][df['name']] = new_data
        else:
            self.historyData['machines'][df['호기']][df['name']] = []
            self.h_initialized[df['호기']].append(df['name'])

    #store searched data
    def store2(self, datalist):
        if datalist[0]['name'] in self.s_initialized[datalist[0]['호기']]:
            self.searchedDataAll['machines'][datalist[0]['호기']][datalist[0]['name']] = datalist
        else:
            self.searchedDataAll['machines'][datalist[0]['호기']][datalist[0]['name']] = []
            self.s_initialized[datalist[0]['호기']].append(datalist[0]['name'])
            self.searchedDataAll['machines'][datalist[0]['호기']][datalist[0]['name']] = datalist

    #store history data
    def store3(self, datalist, dt):
        self.historyData['dt'] = dt
        if datalist[0]['name'] in self.h_initialized[datalist[0]['호기']]:
            self.historyData['machines'][datalist[0]['호기']][datalist[0]['name']] = datalist
        else:
            self.searchedDataAll['machines'][datalist[0]['호기']][datalist[0]['name']] = []
            self.h_initialized[datalist[0]['호기']].append(datalist[0]['name'])
            self.historyData['machines'][datalist[0]['호기']][datalist[0]['name']] = datalist

    def findImportant(self):
        temp = self.getTempData()

        for i in temp['children']:
            for j in i['children']:
                for k in j['children']:
                    for l in k['children']:
                        #t_name = l['name']
                            if l['r'] > float(self.importantThreshold):
                              #  c = self.collections[t_name].find().sort([('_id', -1)]).limit(1)
                                dataFormat = {'호기': i['machine'], '계통': j['name'], '설비': k['name'], 'name': l['name'],
                                          'r': l['r']}
                                self.importantData.append(dataFormat)

    def sortHistoryTag(self):
        #sorted_list = sorted(self.tagImportantList, key=self.tagImportantList.__getitem__, reverse=True)
        taglist = self.tagImportantList
        datalist = sorted(taglist, key=lambda taglist: taglist['val'], reverse=True)
        sorted_list = []
        for i in datalist:
            sorted_list.append(i['data'])
        self.historyData['keys'] = sorted_list
        self.tagImportantList = []

    def tagHistoryList(self, tag, n):
        corr = {}
        if n==5:
            corr = corr5["tags"][tag]
        elif n == 6:
            corr = corr6["tags"][tag]
        elif n == 7:
            corr = corr7["tags"][tag]
        elif n == 8:
            corr = corr8["tags"][tag]

        tag_info = {}

        #self
        stop = stop_keys[tag]
        tag_info[tag] = []
        dates = []
        for s in stop:
            history = stop_history[str(s)]
            tag_info[tag].append( {'name': tag, 'date': history['고장일시'], 'error_type': history['정지구분'], 'correlation': "selected"})
            dates.append(history['고장일시'][0:10])
        for a in corr["affecting"]:
            stop = stop_keys[a]
            tag_info[a] = []
            for s in stop:
                history = stop_history[str(s)]
                tag_info[a].append({'name':a, 'date':history['고장일시'], 'error_type':history['정지구분'], 'correlation':"affecting"})
                dates.append(history['고장일시'][0:10])
        for a in corr["affected"]:
            stop = stop_keys[a]
            tag_info[a] = []
            for s in stop:
                history = stop_history[str(s)]
                tag_info[a].append({'name':a, 'date':history['고장일시'], 'error_type':history['정지구분'], 'correlation':"affected"})
                dates.append(history['고장일시'][0:10])

        unique_date = set(dates)
        dates = list(unique_date)
        dates.sort()
        tag_info["dates"] = dates
        return tag_info

    def getSearchedData(self):
        return self.searchedData

    def getSearchedDataAll(self):
        return self.searchedDataAll

    def getTempData(self):
        return self.tempData

    def getListData(self):
        return self.listData

    def getSimulationListData(self):
        return self.simulationListData

    def getHistoryData(self):
        return self.historyData

    def getPowerData(self):
        return self.powerData

    def getImportantData(self):
        return self.importantData

    def setPowerData(self, power):
        self.powerData = power

class SimulationDataHub(object):
    def __init__(self):
        self.tempData = sample2
        self.historyData = stored2
        self.searchedDataAll = stored2
        self.powerData = {}
        self.searchedData = {}
        self.tagImportantList = []
        self.importantData = {'columns':['호기','계통','설비','name','r','v', 'dt'],'tags':{}}
        self.importantThreshold = 0.7
        #self.historyInit = False
        self.idx = datetime(2015, 1, 1, 0, 0, 0)
        self.idx_step = timedelta(seconds=60) #10
        self.endidx = datetime(2015, 1, 13, 0, 0, 0)
        self.s_initialized = {"1":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[],"9":[],"10":[]} #호기별 태그의 초기화 상태
        self.h_initialized = {"1":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[],"9":[],"10":[]} #호기별 태그의 초기화 상태
        self.simulation = {'start':'','end':'','interval':0}

        logging.info("Simulation Datahub is initated")

    #store the latest data to history data & remove the oldest data
    def store1(self, df):
        self.historyData['dt'] = df['dt']
        form = {"data":{"name":df['name'],"호기":df['호기']},"val":df['r']}
        self.tagImportantList.append(form)

        if df['name'] in self.h_initialized[df['호기']]:
            # store the latest data to history data
            old_data = self.historyData['machines'][df['호기']][df['name']]
            old_data.append(df)
            # remove the oldest data from history data
            new_time = datetime.strptime( df['dt'], '%Y-%m-%d %H:%M:%S')
            old_time = new_time - timedelta(days=1)
            new_data = [item for item in old_data if item['dt'] > str(old_time)]
            self.historyData['machines'][df['호기']][df['name']] = new_data
        else:
            self.historyData['machines'][df['호기']][df['name']] = []
            self.h_initialized[df['호기']].append(df['name'])

    #store searched data
    def store2(self, datalist):
        if datalist[0]['name'] in self.s_initialized[datalist[0]['호기']]:
            self.searchedDataAll['machines'][datalist[0]['호기']][datalist[0]['name']] = datalist
        else:
            self.searchedDataAll['machines'][datalist[0]['호기']][datalist[0]['name']] = []
            self.s_initialized[datalist[0]['호기']].append(datalist[0]['name'])
            self.searchedDataAll['machines'][datalist[0]['호기']][datalist[0]['name']] = datalist

    #store history data (하나씩)
    def store3(self, datalist, dt):
        self.historyData['dt'] = dt
        if datalist[0]['name'] in self.h_initialized[datalist[0]['호기']]:
            self.historyData['machines'][datalist[0]['호기']][datalist[0]['name']] = datalist
        else:
            self.searchedDataAll['machines'][datalist[0]['호기']][datalist[0]['name']] = []
            self.h_initialized[datalist[0]['호기']].append(datalist[0]['name'])
            self.historyData['machines'][datalist[0]['호기']][datalist[0]['name']] = datalist


    def findImportant(self):
        temp = self.getTempData()
        for i in temp['children']:
            for j in i['children']:
                for k in j['children']:
                    for l in k['children']:
                        #t_name = l['name']
                            if l['r'] > float(self.importantThreshold):
                              #  c = self.collections[t_name].find().sort([('_id', -1)]).limit(1)
                                dataFormat = {'호기': i['machine'], '계통': j['name'], '설비': k['name'], 'name': l['name'],
                                          'r': l['r']}
                                self.importantData.append(dataFormat)

    def sortHistoryTag(self):
        #sorted_list = sorted(self.tagImportantList, key=self.tagImportantList.__getitem__, reverse=True)
        taglist = self.tagImportantList
        datalist = sorted(taglist, key=lambda taglist: taglist['val'], reverse=True)
        sorted_list = []
        for i in datalist:
            sorted_list.append(i['data'])
        self.historyData['keys'] = sorted_list
        self.tagImportantList = []

    def tagHistoryList(self, tag, n):
        corr = {}
        if n==5:
            corr = corr5["tags"][tag]
        elif n == 6:
            corr = corr6["tags"][tag]
        elif n == 7:
            corr = corr7["tags"][tag]
        elif n == 8:
            corr = corr8["tags"][tag]

        tag_info = {}
        stop = stop_keys[tag]
        tag_info[tag] = []
        dates = []
        for s in stop:
            history = stop_history[str(s)]
            tag_info[tag].append( {'name': tag, 'date': history['고장일시'], 'error_type': history['정지구분'], 'correlation': "selected"})
            dates.append(history['고장일시'][0:10])
        for a in corr["affecting"]:
            stop = stop_keys[a]
            tag_info[a] = []
            for s in stop:
                history = stop_history[str(s)]
                tag_info[a].append({'name':a, 'date':history['고장일시'], 'error_type':history['정지구분'], 'correlation':"affecting"})
                dates.append(history['고장일시'][0:10])
        for a in corr["affected"]:
            stop = stop_keys[a]
            tag_info[a] = []
            for s in stop:
                history = stop_history[str(s)]
                tag_info[a].append({'name':a, 'date':history['고장일시'], 'error_type':history['정지구분'], 'correlation':"affected"})
                dates.append(history['고장일시'][0:10])

        unique_date = set(dates)
        dates = list(unique_date)
        dates.sort()
        tag_info["dates"] = dates
        return tag_info

    def getSearchedData(self):
        return self.searchedData

    def getSearchedDataAll(self):
        return self.searchedDataAll

    def getTempData(self):
        return self.tempData

    def getHistoryData(self):
        return self.historyData

    def getPowerData(self):
        return self.powerData

    def getImportantData(self):
        return self.importantData

    def setPowerData(self, power):
        self.powerData = power

class MongoConnection(object):
    def __init__(self):
        self.client = MongoClient(settings.DATABASES['mongo']['HOST'], settings.DATABASES['mongo']['PORT'])
        #self.db = client[settings.DATABASES['mongo']['NAME']]
        self.db = self.client['predict_150114']
        self.collections = {}   #dictionary
        self.power_collection = self.client['kewp_power_setting']['kewp_5th']
        self.important_db = self.client['important_tag']
        self.db_predict = self.client['predict_150114']
        self.stop_collection = self.client['stop_history']
        self.col_list = self.db.collection_names()
        self.tag_info = self.client[settings.DATABASES['mongo']['NAME']]['KEWP_ALL_TAG']
        self.mapping = {"가열기": 0, "보일러": 1, "통풍": 2, "복급수": 3}
        self.s_list = [['FWH', 'HTR'], ['BUR', 'CRH', 'ECO', 'FUR', 'HRH', 'RH', 'SB', 'SEPA', 'SH', 'WALL TUBE'],
                  ['BTU', 'CIDF', 'EP', 'FDF', 'FLUE GAS', 'FUR', 'GAH', 'IDF', 'PAF', 'PULV', 'SA', 'STACK', 'WB'],
                  ['BFP', 'BFPM', 'BFPT', 'COND', 'COP']]
        self.data_obj = DataHub()
        #self.simul_obj = SimulationDataHub()
        #make connection with all collections
        for tag in self.col_list:
            self.get_collections(tag)
        #self.InitloadImportant()
        self.InitloadJsonData()
        self.loadHistoryData()
        logging.info("MongoConnection is initated")
        poll_thread = threading.Thread(target=self.polling)
        poll_thread.daemon = True
        poll_thread.start()
        logging.info("Poll Thred Start")

    def polling(self):
        while True:
            logging.debug("Index : " + str(self.data_obj.idx))
            self.data_obj.idx += self.data_obj.idx_step # POLLING
            #self.loadJsonData() 분석시스템에서 사용
            self.loadListData() #대쉬보드 시스템에서 사용
            time.sleep(60)

    # Search specific data (p day)
    def searchDateAll(self, dt, dt2):
        for tag in self.col_list:
            c = self.tag_info.find_one({'Tag name': tag})
            if tag != 'KEWP_ALL_TAG' and tag in self.col_list and c != None:
                datalist = []
                cursor = self.find3(tag, dt, dt2)
                for i in cursor:
                    v = i['val']
                    if math.isnan(v):
                        v = 0
                    dataFormat = {'호기': c['호기'], '계통': c['계통'], '설비': c['설비'], 'name': c['Tag name'], 'r': i['prob'],
                                  'v': v, "dt": i['Date'], "prediction":i['prediction']}
                    datalist = [dataFormat] + datalist

                self.data_obj.store2(datalist)

    def InitloadJsonData(self):
        #Make Sample Tree structure
        for n in range(4):
            tag_list = {
                "name": str(n + 5) + "호기", "machine": str(n + 5), "children": [
                    {"name": "가열기", "machine": str(n + 5), "children": []},
                    {"name": "보일러", "machine": str(n + 5), "children": []},
                    {"name": "통풍", "machine": str(n + 5), "children": []},
                    {"name": "복급수", "machine": str(n + 5), "children": []}
                ]
            }
            for i in range(4):
                for j in self.s_list[i]:
                    tag_list['children'][i]['children'].append(
                        {'name': j, 'machine': str(n + 5), 'children': []})

            for t_name in self.col_list:
                if self.tag_info.find({'Tag name': t_name}).count() != 0:  # Check tag has information or not
                    tag = self.tag_info.find({'Tag name': t_name})
                    c = self.collections[t_name].find({'Date': str(self.data_obj.idx)})  # POLLING : 일단 앞부터 순서대로
                    v = c[0]['val']
                    if math.isnan(v):
                        v = 0

                    name_list = list(tag[0]['Tag name'])

                    if n == 1:
                        if name_list[5] == '3':
                            name_list[5] = '3'
                            name_list[6] = '6'
                        else:
                            name_list[5] = '6'
                    elif n == 2:
                        if name_list[5] == '3':
                            name_list[5] = '4'
                            name_list[6] = '7'
                        else:
                            name_list[5] = '7'
                    elif n == 3:
                        if name_list[5] == '3':
                            name_list[5] = '4'
                            name_list[6] = '8'
                        else:
                            name_list[5] = '8'

                    tag_name = "".join(name_list)

                    if tag[0]['Des'] == None:
                        tag[0]['Des'] = ""
                    data = {'name': tag_name, 'machine': str(n + 5), '호기': str(n + 5), '계통': tag[0]['계통'],
                            '설비': tag[0]['설비'], 'Des': tag[0]['Des'], 'Temp': tag[0]['Temp'], 'Count': tag[0]['Count'],
                            'r': c[0]['prob'], 'v':v, 'p':c[0]['prediction']}
                    # if tag[0]['설비'] in s_list[mapping[tag[0]['계통']]]:
                    m_id = self.mapping[tag[0]['계통']]
                    s_id = self.s_list[m_id].index(tag[0]['설비'])
                    tag_list['children'][m_id]['children'][s_id]['children'].append(data)
                    #   else:
                    #       s_list[mapping[tag[0]['계통']]].append(tag[0]['설비'])
                    #       tag_list['children'][mapping[tag[0]['계통']]]['children'].append({'name':tag[0]['설비'],'children':[]})
                    #       idx = s_list[mapping[tag[0]['계통']]].index(tag[0]['설비'])
                    #       tag_list['children'][mapping[tag[0]['계통']]]['children'][idx]['children'].append(data)

            self.data_obj.tempData['children'].append(tag_list)

       # self.data_obj.sortHistoryTag()
        logging.info("JSON Tree sturcture is initated")

    #important DB로 부터 dt시간 이후의 중요 리스트 불러와서 로컬 변수 importantData에 저장
    def InitloadImportant(self):
        dt = datetime(2015, 1, 10, 0, 0, 0) #should change : 현재로부터 하루전, 혹은 지정일.
        col_list = self.important_db.collection_names()
        for tag in col_list:
            cursor = self.important_db[tag].find({"dt" : {'$gte': str(dt)}})

            for c in cursor:
                dataFormat = {'호기': c['호기'], '계통': c['계통'], '설비': c['설비'], 'name': c['name'], 'r': c['r'],
                              'v': c['v'], "dt": c['dt'], "c": c['p']}

                if tag not in self.data_obj.importantData['tags']:
                    self.data_obj.importantData['tags'][tag] = []

                self.data_obj.importantData['tags'][tag].append(dataFormat)

        logging.info("Important data is initated")

    #고장확률 높은 데이터만
    def loadListData(self):
        self.data_obj.listData = {"plant":{"1":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[],"9":[],"10":[]}}
        for t_name in self.col_list:
            if self.tag_info.find({'Tag name': t_name}).count() != 0:  # Check tag has information or not
                tag = self.tag_info.find({'Tag name': t_name})
                # c = self.collections[t_name].find().sort([('_id',-1)]).limit(1) #POLLING : 마지막 (최근) 값
                c = self.collections[t_name].find({'prob': {'$gt': float(self.data_obj.importantThreshold)},'Date': str(self.data_obj.idx)})  # 일단 앞부터 순서대로
                if c.count() > 0 :
                    v = c[0]['val']
                    if math.isnan(v):
                        v = 0

                    # thresohold 보다 높을 시 listData에 저장  중요데이터에 저장
                    dataFormat = {'name': tag[0]['Tag name'], '호기': tag[0]['호기'], '계통': tag[0]['계통'], '설비': tag[0]['설비'],  'r': c[0]['prob'], 'v': v, 'p':c[0]['prediction'],'dt': c[0]['Date'] }
                    self.data_obj.listData["plant"][tag[0]['호기']].append(dataFormat)

                    #Local 변수 importantData 에 추가
                    if tag[0]['Tag name'] not in self.data_obj.importantData['tags']:
                        self.data_obj.importantData['tags'][dataFormat['name']] = []

                    self.data_obj.importantData['tags'][dataFormat['name']].append(dataFormat)

                    #important DB 에 저장
                    obj = {'name': dataFormat['name'], '호기': dataFormat['호기'], '계통': tag[0]['계통'], '설비': tag[0]['설비'],  'r': c[0]['prob'], 'v': v, 'p':c[0]['prediction'],'dt': c[0]['Date'] }
                    col_obj.update_important(col_obj.important_db, dataFormat['name'], obj) #서버용
                    #col_obj.update_important(self.client['important_tag'], tag[0]['Tag name'], obj) #로컬용


    #i:호기, j:계통, k:설비, l:태그
    #Update 'r'
    def loadJsonData(self):
        for i in self.data_obj.tempData['children']:
            for j in i['children']:
                for k in j['children']:
                    for l in k['children']:
                        t_name = l['name']
                        if t_name in self.col_list:
                            # c = self.collections[t_name].find().sort([('_id',-1)]).limit(1) #POLLING :마지막 (최근) 값
                            c = self.collections[t_name].find({'Date': str(self.data_obj.idx)})  # 일단 앞부터 순서대로
                            v = c[0]['val']
                            l['r'] = c[0]['prob']
                            if math.isnan(v):
                                v = 0

                            dataFormat = {'호기': i['machine'], '계통': j['name'], '설비': k['name'], 'name': l['name'],
                                          'r': l['r'], 'v': v, 'p':c[0]['prediction'],'dt': c[0]['Date']}

                            # 정시 (1시간 단위만 업데이트)
                            date_form = datetime.strptime(dataFormat['dt'], '%Y-%m-%d %H:%M:%S')
                            if date_form.minute == 0 & date_form.second == 0:
                                self.data_obj.store1(dataFormat)

                            # thresohold 보다 높을 시 중요데이터에 저장
                            if l['r'] > float(self.data_obj.importantThreshold):
                                if dataFormat['name'] not in self.data_obj.importantData['tags']:
                                    self.data_obj.importantData['tags'][dataFormat['name']] = []

                                self.data_obj.importantData['tags'][dataFormat['name']].append(dataFormat)

                                # important DB 에 저장
                                obj = {'호기': i['machine'], '계통': j['name'], '설비': k['name'], 'name': l['name'],
                                              'r': l['r'], 'v': v, 'p':c[0]['prediction'],'dt': c[0]['Date']}
                                col_obj.update_important(col_obj.important_db, dataFormat['name'], obj) #서버용
                                #col_obj.update_important(self.client['important_tag'], dataFormat['name'], obj)  # 로컬용

        self.data_obj.sortHistoryTag()

    #Search the latest data from dt
    def loadHistoryData(self):
        dt = datetime(2015, 1, 12, 0, 0, 0)
        dt2 = datetime(2015, 1, 13, 0, 0, 0)

        for tag in self.col_list:
            c = self.tag_info.find_one({'Tag name': tag})
            if tag != 'KEWP_ALL_TAG' and c != None:
                datalist = []
                cursor = self.find3(tag, dt, dt2)
                count = 0
                for i in cursor:
                    date_form = datetime.strptime(i['Date'], '%Y-%m-%d %H:%M:%S')
                    if date_form.minute == 0 & date_form.second == 0:
                        count += 1
                        v = i['val']
                        if math.isnan(v):
                            v = 0

                        dataFormat = {'호기': c['호기'], '계통': c['계통'], '설비': c['설비'], 'name': c['Tag name'], 'r': i['prob'],
                                          'v': v, "dt":i['Date'],'p':i['prediction']}
                        datalist = datalist + [dataFormat]

                        #the last data SHOULD CHANGE when db is changed
                        if count==24:
                            form = {"data": {"name": dataFormat['name'], "호기": dataFormat['호기']},"val": dataFormat['r'],'predict':dataFormat['p']}
                            self.data_obj.tagImportantList.append(form)

                self.data_obj.store3(datalist, i['Date'])

        self.data_obj.sortHistoryTag()
        logging.info("History data is initated")

    #고장확률 높은 데이터만 (시뮬용이라 시간범위를 sequence로)
    def loadSimulationListData(self):
        self.data_obj.simulationListData = {}
        for t_name in self.col_list:
            if self.tag_info.find({'Tag name': t_name}).count() != 0:  # Check tag has information or not
                tag = self.tag_info.find({'Tag name': t_name})
                cursor = self.collections[t_name].find({'prob': {'$gt': float(self.simul_obj.importantThreshold)},'Date':{'$gte':str(self.simul_obj.idx),'$lt' : str(self.simul_obj.endidx)}})

                if cursor.count() > 0 :
                    for c in cursor:
                        v = c['val']
                        if math.isnan(v):
                            v = 0

                        dataFormat = {'호기': tag[0]['호기'], '계통': tag[0]['계통'], '설비': tag[0]['설비'],
                                      'name': tag[0]['Tag name'], 'r': c['prob'], 'v': v, 'p':c['prediction'],'dt': c['Date'], }


                        if not str(c['Date']) in self.data_obj.simulationListData:
                            self.data_obj.simulationListData[str(c['Date'])] = {"plant":{"1":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[],"9":[],"10":[]}}

                        self.data_obj.simulationListData[str(c['Date'])]["plant"][tag[0]['호기']].append(dataFormat)

                          # Important Tags
                          #  if dataFormat['name'] in self.simul_obj.importantData['tags']:
                          #      self.simul_obj.importantData['tags'][dataFormat['name']].append(dataFormat)
                          #  else:
                          #      self.simul_obj.importantData['tags'][dataFormat['name']] = []
                          #      self.simul_obj.importantData['tags'][dataFormat['name']].append(dataFormat)
        #sort by time
        self.data_obj.simulationListData = dict(collections.OrderedDict(sorted(self.data_obj.simulationListData.items())))
        # important list new format
        # self.data_obj.importantData[str(dataFormat['dt'])] = {'tags':important_list, 'threshold':self.data_obj.importantThreshold}
        logging.debug("From : " + str(self.simul_obj.idx) +" to : "+ str(self.simul_obj.endidx))

    def loadSimulationJsonData(self):
        for i in self.simul_obj.tempData['children']:
            for j in i['children']:
                for k in j['children']:
                    for l in k['children']:
                        t_name = l['name']
                        if t_name in self.col_list:
                            #c = self.collections[t_name].find().sort([('_id',-1)]).limit(1) #마지막 (최근) 값
                            cursor = self.collections[t_name].find({'Date':str(self.simul_obj.idx)}) # 일단 앞부터 순서대로

                            cursor_len = cursor.count()

                            if cursor_len > 0 :
                                v = cursor[0]['val']
                                l['r'] = cursor[0]['prob']
                                #R value
                                if math.isnan(v):
                                    v = 0


                                dataFormat = {'호기':i['machine'],'계통':j['name'],'설비':k['name'],'name':l['name'],'r':l['r'], 'v':v, 'p':cursor[0]['val']['prediction'],'dt':cursor[0]['Date'],}

                                #정시 (1시간 단위만 업데이트)
                                date_form = datetime.strptime(dataFormat['dt'], '%Y-%m-%d %H:%M:%S')
                                if date_form.minute == 0 & date_form.second == 0:
                                    self.simul_obj.store1(dataFormat)

                                #thresohold 보다 높을 시 중요데이터에 저장
                                if l['r'] > float(self.simul_obj.importantThreshold):
                                    if dataFormat['name'] in self.simul_obj.importantData['tags']:
                                        self.simul_obj.importantData['tags'][dataFormat['name']].append(dataFormat)
                                    else:
                                        self.simul_obj.importantData['tags'][dataFormat['name']] = []
                                        self.simul_obj.importantData['tags'][dataFormat['name']].append(dataFormat)
                                    #important_list.append(dataFormat)

        #important list new format
        #self.simul_obj.importantData[str(dataFormat['dt'])] = {'tags':important_list, 'threshold':self.simul_obj.importantThreshold}
        logging.debug("Index : " + str(self.simul_obj.idx))
        self.simul_obj.idx += self.simul_obj.idx_step
        self.simul_obj.sortHistoryTag()

    #one day before from simulation start date
    def loadSimulationHistoryData(self):
        dt2 = self.simul_obj.simulation['start']
        dt = dt2 - timedelta(days=1)
        for tag in self.col_list:
            c = self.tag_info.find_one({'Tag name': tag})
            if tag != 'KEWP_ALL_TAG' and c != None:
                datalist = []
                cursor = self.find3(tag, dt, dt2)

                count = 0
                if cursor.count() > 0 :
                    for i in cursor:
                        date_form = datetime.strptime(i['Date'], '%Y-%m-%d %H:%M:%S')
                        if date_form.minute == 0 & date_form.second == 0:
                            count += 1
                            v = i['val']
                            if math.isnan(v):
                                v = 0

                            dataFormat = {'호기': c['호기'], '계통': c['계통'], '설비': c['설비'], 'name': c['Tag name'], 'r': i['prob'],
                                              'v': v, "dt":i['Date'],'p':i['prediction']}
                            datalist = datalist + [dataFormat]

                            #the last data SHOULD CHANGE when db is changed
                            if count==24:
                                form = {"data": {"name": dataFormat['name'], "호기": dataFormat['호기']},"val": dataFormat['r'],"predict":dataFormat['p']}
                                self.simul_obj.tagImportantList.append(form)

                    self.simul_obj.store3(datalist, i['Date'])

        self.simul_obj.sortHistoryTag()
        logging.info("Simulation History data is loaded")

class MongoCollection(MongoConnection):
    def __init__(self):
        super(MongoCollection, self).__init__()
        logging.info("Collection is initated")

    def update_important(self, targetDB, tag, obj):
       targetDB[tag].insert(obj)
       # if self.collections[tag].find({'id': obj.id}).count():
       #     self.collections[tag].update({'id': obj.id},{'id':123,'name':'test'})
       # else:
       #     self.collections[tag].insert_one({'id':123,'name':'test'})

    def remove(self, tag, obj):
        if self.collections[tag].find({'id': obj.id}).count():
            self.collections[tag].delete_one({'id': obj.id})

    def find(self, tag, n):
        #get the last N documents
        return self.collections[tag].find({}).limit(n)

    def find2(self, tag, dt):
        #get the data after dt
        return self.collections[tag].find({"Date" : {'$gte': str(dt)}})

    def find3(self, tag, dt, dt2):
        #get the data from dt ~ dt2
        return self.collections[tag].find({ "Date" : {'$gte': str(dt),'$lt' : str(dt2)} })

    def get_collections(self, tag):
        self.collections[tag] = self.db[tag]

# Global object
col_obj = MongoCollection()
