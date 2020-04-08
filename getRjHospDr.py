#!/usr/bin/python
#-*- coding:utf-8 -*-

import urllib.request
import urllib.parse
import os, sys, getopt, threading, time, ssl, json;
from datetime import datetime, timedelta;

#瑞金医院专家门诊

#当使用urllib模块访问https网站时，由于需要提交表单，而python3默认是不提交表单的，所以这时只需在代码中加上以下代码即可
ssl._create_default_https_context = ssl._create_unverified_context

#根据专家号key以及门诊名来获取
#内分泌科 王卫庆 主任医师 key=JdczJZhC9pLkbQ2Xdn6NnQ== deptName=1xV5qALiVlPluu5mIoBC4g==
def getDrSchedule(drKey=None, deptName=None, registerType="tkXLN7TbvFA="):
    if drKey is None:
        return None;
    if deptName is None:
        return None;
    url = "https://psapp.rjh.com.cn/ruijin-web/ruijin/apply/getReservationDetail";
    head = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    #reqJson = {"deptName": deptName,"registerType": registerType,"key": drKey}
    #request = urllib.request.Request(url, json.dumps(reqJson).encode('utf-8'), headers=head);
    reqJson = "deptName=" + deptName + "&registerType=" + registerType + "&key=" + drKey;
    request = urllib.request.Request(url, reqJson.encode("utf-8"), headers=head);
    try:
        with urllib.request.urlopen(request) as f:
            respText = f.read().decode('utf-8');
            respJson = json.loads(respText);
            return respJson;
    except urllib.error.HTTPError as e:
        print(e)
        print("get getDrSchedule Request error");
        return None;

def dealDrScheduleInfo(infoJson=None):
    hasSchedule = {};
    if infoJson is None:
        return None;
    if ("Body" in infoJson) is False:
        return None;
    if ("TimeInfo" in infoJson["Body"]) is False:
        return None;
    for index in range(len(infoJson["Body"]["TimeInfo"])):
        if ("ResourceNumber" in infoJson["Body"]["TimeInfo"][index]):
            ResourceNumber = int(infoJson["Body"]["TimeInfo"][index]["ResourceNumber"]);
            if ResourceNumber > 0:
                #医生姓名 Target=陶蓓
                if "Target" in infoJson["Body"]:
                    hasSchedule["DoctorName"] = infoJson["Body"]["Target"];
                #可预约科室 DeptName=门诊内分泌
                if "DeptName" in infoJson["Body"]:
                    hasSchedule["DeptName"] = infoJson["Body"]["DeptName"];
                #医生级别 Grade=副主任医师
                if "Grade" in infoJson["Body"]:
                    hasSchedule["DoctorLevelName"] = infoJson["Body"]["Grade"];
                #可预约日期 Target2=2020-04-09
                hasSchedule["Groups"] = infoJson["Body"]["TimeInfo"][index]["Target2"];
                #可预约时间 Target3=08:00-08:59
                hasSchedule["StartTime"] = infoJson["Body"]["TimeInfo"][index]["Target3"];
                #剩余可约号数 ResourceNumber=0
                hasSchedule["AvailableBook"] = infoJson["Body"]["TimeInfo"][index]["ResourceNumber"];
                #挂号价格 Fee=50.00
                hasSchedule["Price"] = infoJson["Body"]["TimeInfo"][index]["Fee"];
                return hasSchedule
    return None;

def startMe(drKey=None, deptName=None):
    drSchedule = getDrSchedule(drKey, deptName);
    drAvailable = dealDrScheduleInfo(drSchedule);
    print(drAvailable)
    availableText = None;
    if drAvailable is not None:
        availableText = drAvailable["Groups"] + ", ";
        availableText += "瑞金医院, ";
        availableText += drAvailable["DeptName"] + ", ";
        availableText += drAvailable["DoctorName"];
        availableText += "(" + drAvailable["DoctorLevelName"] + "), ";
        availableText += "可预约: ";
        availableText += drAvailable["StartTime"] + ", ";
        availableText += "剩余" + drAvailable["AvailableBook"] + "位, ";
        availableText += "挂号费" + drAvailable["Price"] + "元";
    print(availableText);
    return availableText;

def newThread(drKey=None, deptName=None):
    t = threading.Thread(target=startMe, args=(drKey, deptName), name='startMeThread')
    t.start()
    #进程启动需要设置sleep迫使其后台运行
    time.sleep(1)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hk:n:");
    except:
        print ('please try use -k to input doctor Number')
        print ('please try use -n to input department Number')
        sys.exit(2)
    
    if(opts is None) or (len(opts) < 1):
        if len(argv) > 0:
            newThread(argv[0], argv[1]);
        else:
            newThread();
        return;
    
    deptNum = None
    for op, value in opts:
        if op == "-h":
            print ('please try use -k to input doctor Number')
            print ('please try use -n to input department Number')
            sys.exit()
        if op == "-k":
            drKey = value;
        if op == "-n":
            deptName = value;
       
    newThread(drKey, deptName);
		
if __name__ == "__main__":
    main(sys.argv[1:])