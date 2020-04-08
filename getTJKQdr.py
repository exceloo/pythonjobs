#!/usr/bin/python
#-*- coding:utf-8 -*-

import urllib.request
import urllib.parse
import os, sys, getopt, threading, time, json;
from datetime import datetime, timedelta;

#同济大学附属口腔医院医生排班信息

#获取科室排版
#deptNum = 83 DeptName=牙体牙髓病一科
#deptNum = 85 DeptName=牙体牙髓病二科
def getDeptSchedule(deptNum=None):
    if deptNum is None:
        return None;
    url = "http://open.cmsfg.com/api/appointment/Scheduling?AppId=501111";
    startDate = datetime.now().strftime("%Y-%m-%d");
    endDate = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d");
    # "method":"GetHisSchedulingDoctorList" "RegisterType":"0","AppointmentType":"0" 专家
    # "method":"GetHisDeptScheduling" "RegisterType":"1,2","AppointmentType":"1,2" 普通门诊
    reqJson = {
        "method":"GetHisSchedulingDoctorList",
        "params":[{
            "AppId":"501111",
            "RegisterType":"1,2",
            "AppointmentType":"1,2",
            "DeptCode":str(deptNum),
            "Date":startDate,
            "EndDate":endDate,
            "IsScheduleFilter": False
        }]
    }
    request = urllib.request.Request(url, json.dumps(reqJson).encode('utf-8'), {});
    try:
        with urllib.request.urlopen(request) as f:
            respText = f.read().decode('utf-8');
            respJson = json.loads(respText);
            return respJson;
    except:
        print("get getDeptSchedule Request error");
        return None;

def dealDeptSchedule(infoJson=None):
    dealedInfo = [];
    if infoJson is None:
        return None;
    if ("result" in infoJson) is False:
        return None;
    for index in range(len(infoJson["result"])):
        if infoJson["result"][index]["AppointmentDate"] is not None:
            dealedInfo.insert(0, infoJson["result"][index]);
    if len(dealedInfo)<1:
        return None;
    return dealedInfo;

def getDrSchedule(drWorkNum=None):
    if drWorkNum is None:
        return None;  
    url = "http://open.cmsfg.com/api/appointment/Scheduling?AppId=501111";
    startDate = datetime.now().strftime("%Y-%m-%d");
    endDate = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d");
    reqJson = {
        "method":"GetScheduling",
        "params":[{
            "AppId":"501111",
            "DoctorWorkNum": str(drWorkNum),
            "RegisterType":"1,2",
            "AppointmentType":"1,2",
            "Date":startDate,
            "EndDate":endDate
        }]
    }
    request = urllib.request.Request(url, json.dumps(reqJson).encode('utf-8'), {});
    try:
        with urllib.request.urlopen(request) as f:
            respText = f.read().decode('utf-8');
            respJson = json.loads(respText);
            return respJson;
    except:
        print("get getDrSchedule Request error");
        return None;

def dealDrScheduleInfo(infoJson=None):
    hasSchedule = {};
    if infoJson is None:
        return None;
    if ("result" in infoJson) is False:
        return None;
    if ("AppointmentScheduling" in infoJson["result"]) is False:
        return None;
    for index in range(len(infoJson["result"]["AppointmentScheduling"])):
        if ("Schedulings" in infoJson["result"]["AppointmentScheduling"][index]):
            Schedulings = infoJson["result"]["AppointmentScheduling"][index]["Schedulings"]
            for sch_index in range(len(Schedulings)):
                #Appointment已预约人数
                #CanAppointment总共可预约人数
                if Schedulings[sch_index]["CanAppointment"] > Schedulings[sch_index]["Appointment"]:
                    #可预约日期
                    hasSchedule["Groups"] = infoJson["result"]["AppointmentScheduling"][index]["Groups"];
                    #可预约时间
                    hasSchedule["StartTime"] = Schedulings[sch_index]["StartTime"];
                    #剩余可约号数
                    hasSchedule["AvailableBook"] = str(Schedulings[sch_index]["CanAppointment"] - Schedulings[sch_index]["Appointment"]);
                    #挂号价格
                    hasSchedule["Price"] = str(Schedulings[sch_index]["Price"]);
                    return hasSchedule
    return None;

def startMe(deptNum=None, T=None):
    deptSchedule = getDeptSchedule(deptNum);
    availableText = None;
    doctor = None;
    if deptSchedule is None:
        return None;
    deptDrArray = dealDeptSchedule(deptSchedule);
    if deptDrArray is None:
        return None;
    for index in range(len(deptDrArray)):
        drSchedule = getDrSchedule(deptDrArray[index]["DoctorWorkNum"]);
        drAvailable = dealDrScheduleInfo(drSchedule);
        if drAvailable is not None:
            availableText = drAvailable["Groups"] + ", ";
            availableText += deptDrArray[index]["DeptName"] + ", ";
            availableText += deptDrArray[index]["DoctorName"];
            availableText += "(" + deptDrArray[index]["DoctorLevelName"] + "), ";
            availableText += "可预约: ";
            availableText += drAvailable["StartTime"] + ", ";
            availableText += "剩余" + drAvailable["AvailableBook"] + "位, ";
            availableText += "挂号费" + drAvailable["Price"] + "元";
    print(availableText);
    return availableText;

def newThread(deptNum=None, T=None):
    t = threading.Thread(target=startMe, args=(deptNum, T), name='startMeThread')
    t.start()
    #进程启动需要设置sleep迫使其后台运行
    time.sleep(1)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hn:");
    except:
        print ('please try use -n to input Doctor Number')
        sys.exit(2)
    
    if(opts is None) or (len(opts) < 1):
        if len(argv) > 0:
            newThread(argv[0]);
        else:
            newThread();
        return;
    
    deptNum = None
    for op, value in opts:
        if op == "-h":
            print ('please try use -n to input Doctor Number')
            sys.exit()
        
        if op == "-n":
            deptNum = value;
       
    newThread(deptNum);
		
if __name__ == "__main__":
    main(sys.argv[1:])