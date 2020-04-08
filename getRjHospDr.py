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
    scheduleList = [];
    if infoJson is None:
        return None;
    if ("Body" in infoJson) is False:
        return None;
    if(infoJson["Body"] is None):
        return None;
    if ("TimeInfo" in infoJson["Body"]) is False:
        return None;
    dayList = ["周一","周二","周三","周四","周五","周六","周日"];
    for index in range(len(infoJson["Body"]["TimeInfo"])):
        if ("ResourceNumber" in infoJson["Body"]["TimeInfo"][index]):
            currentTimeItem = infoJson["Body"]["TimeInfo"][index];
            ResourceNumber = int(currentTimeItem["ResourceNumber"]);
            if ResourceNumber > 0:
                hasSchedule = {};
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
                hasSchedule["Groups"] = currentTimeItem["Target2"];
                hasSchedule["GroupsNum"] = int(time.mktime(time.strptime(currentTimeItem["Target2"], '%Y-%m-%d')))
                #科预约周几 Target1=周二
                if currentTimeItem["Target1"] in dayList:
                    hasSchedule["Day"] = currentTimeItem["Target1"];
                    hasSchedule["DayNum"] = len(dayList) - dayList.index(currentTimeItem["Target1"]);
                #可预约时间 Target3=08:00-08:59
                hasSchedule["StartTime"] = currentTimeItem["Target3"];
                #获取开始时间
                hasSchedule["StartNum"] = 24 - int(currentTimeItem["Target3"][0:2]);
                #剩余可约号数 ResourceNumber=0
                hasSchedule["AvailableBook"] = currentTimeItem["ResourceNumber"];
                #挂号价格 Fee=50.00
                hasSchedule["Price"] = currentTimeItem["Fee"];
                hasSchedule["PriceNum"] = int(currentTimeItem["Fee"][:-3]);
                scheduleList.insert(0, hasSchedule);
    if len(scheduleList) > 0:
        return scheduleList
    return None;

def startMe(drKey=None, deptName=None):
    drSchedule = getDrSchedule(drKey, deptName);
    drAvailableList = dealDrScheduleInfo(drSchedule);
    availableText = None;
    if drAvailableList is not None:
        drAvailable = drAvailableList[0];
        availableText = drAvailable["Groups"] + ", ";
        availableText += drAvailable["Day"] + ", ";
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

def startMeList(drList = None):
    availableText = None;
    if drList is None:
        return None;
    if len(drList) < 1:
        return None;
    
    drTotalList = [];
    #累加所有可选医生的排版
    for index in range(len(drList)):
        drSchedule = getDrSchedule(drList[index]["key"], drList[index]["deptName"]);
        drAvailableList = dealDrScheduleInfo(drSchedule);
        if (drAvailableList is not None) and (len(drAvailableList) > 0):
            drTotalList += drAvailableList;

    if(len(drTotalList)<1):
        return None;
    #重新排序 排序优先级： 低价，晚些时间，周末，早些日期
    newLlist = sorted(drTotalList, key=lambda ele:(ele["PriceNum"], ele["StartNum"], ele["DayNum"], ele["GroupsNum"]));

    #文字输出
    availableText = "瑞金医院" + "\r\n\r\n";
    for index in range(len(newLlist)):
        currentDr = newLlist[index];
        availableText += currentDr["Groups"] + ", ";
        availableText += currentDr["Day"] + ", ";
        availableText += currentDr["DeptName"] + ", ";
        availableText += currentDr["DoctorName"];
        availableText += "(" + currentDr["DoctorLevelName"] + "), ";
        availableText += "可预约: ";
        availableText += currentDr["StartTime"] + ", ";
        availableText += "剩余" + currentDr["AvailableBook"] + "位, ";
        availableText += "挂号费" + currentDr["Price"] + "元";
        availableText += "\r\n\r\n";

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