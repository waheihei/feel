#!/bin/python
# -*- coding:utf-8 -*-
import urllib
import urllib2
import base64
import hmac
import urllib
import time
import uuid
import random
from hashlib import sha1
import datetime
import sys
import os
import json
from xlwt import Workbook

dbinstanceid="rdslar1ybyb9fwan7np3"
#--------------
Format="json"
Version=str("2014-08-15")
SignatureMethod="HMAC-SHA1"
SignatureVersion=str("1.0")
AccessKeyId="3vmC4egrWnLrS4Dm"
AccessKeySecret="Ph8Ogen8iy6JuQbxayBzbGO9Wdj19M"
OwnerId=str("12345678")
PageSize=str(30)


book = Workbook()
sheet1 = book.add_sheet('RDS_slowlog')
sheet1.write(0,0,'ReturnRowCounts')
sheet1.write(0,1,'HostAddress')
sheet1.write(0,2,'SQLText')
sheet1.write(0,3,'LockTimes')
sheet1.write(0,4,'ExecutionStartTime')
sheet1.write(0,5,'ParseRowCounts')
sheet1.write(0,6,'QueryTimes')
sheet1.write(0,7,'DBName')
row1 = sheet1.row(2)
sheet1.col(2).width = 10000

def url_connect(parameters):
    #sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])
    canonicalizedQueryString = ''
    for k in parameters.keys():
        canonicalizedQueryString += '&' + k + '=' + parameters[k]
    return canonicalizedQueryString[1:]
def sign(accessKeySecret, parameters):
    sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])
    canonicalizedQueryString = ''
    for (k, v) in sortedParameters:
        canonicalizedQueryString += '&' + percent_encode(k) + '=' + percent_encode(v)
    stringToSign = 'GET&%2F&' + percent_encode(canonicalizedQueryString[1:])
    h = hmac.new(accessKeySecret + "&", stringToSign, sha1)
    signature = base64.encodestring(h.digest()).strip()
    signature = percent_encode(signature)
    return signature
'''转码'''
def percent_encode(encodeStr):
    encodeStr = str(encodeStr)
    res = urllib.quote(encodeStr.decode('utf-8').encode('utf-8'), '')
    res = res.replace('+', '%20')
    res = res.replace('*', '%2A')
    res = res.replace('%7E', '~')
    res = res.replace('=', '%3D')
    res = res.replace('/', '%2F')
    return res
def select_sqlslow(pagenum):
    PageNumber=str(pagenum)
    now_time = datetime.datetime.now()
    yesterday = now_time + datetime.timedelta(minutes= -960)
    #yesterday = now_time + datetime.timedelta(days=-2)
    #tmstp = now_time + datetime.timedelta(seconds= -10)
    #StartTime=time.strftime("%Y-%m-%dT%H:%MZ",yesterday)
    StartTime=yesterday.strftime("%Y-%m-%dT%H:%MZ")
    EndTime=now_time.strftime("%Y-%m-%dT%H:%MZ")
    #---------rand
    ##randnum=(1000 * random() + 100 * random() + 10 * random())
    SignatureNonce=str(uuid.uuid1())
    #---------sign
    Timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
    parameters = {
        "Action": "DescribeSlowLogRecords",
        "DBInstanceId": dbinstanceid ,
        "StartTime": StartTime ,
        "EndTime": EndTime ,
        "PageSize":PageSize,
        "PageNumber":PageNumber,
        "Format": Format ,
        "Version": Version,
        "SignatureMethod": "HMAC-SHA1",
        "SignatureNonce": SignatureNonce ,
        "SignatureVersion": "1.0" ,
        "AccessKeyId": AccessKeyId ,
        "Timestamp": Timestamp
    }
    Signature = sign(AccessKeySecret, parameters)
    #---------Action=DescribeSlowLogRecords
    url_record_data="DBInstanceId=" + dbinstanceid + \
             "&StartTime=" + StartTime + \
             "&EndTime=" + EndTime + \
             "&PageSize=" + PageSize + \
             "&PageNumber=" + PageNumber + \
             "&Format=" + Format + \
             "&Version=" + Version + \
             "&Signature=" + Signature + \
             "&SignatureMethod=HMAC-SHA1" \
             "&SignatureNonce=" + SignatureNonce + \
             "&SignatureVersion=1.0" \
             "&AccessKeyId=" + AccessKeyId + \
             "&Timestamp=" + Timestamp
    #url = "https://rds.aliyuncs.com/?Action=DescribeSlowLogs&"
    url_record = "https://rds.aliyuncs.com/?Action=DescribeSlowLogRecords&" \
          + url_record_data
    req = urllib2.Request(url_record)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res

def create_xls(res):
    data = json.loads(res)
    list = data['Items']['SQLSlowRecord']
    j = 1
    for i in list:
        ReturnRowCounts = i['ReturnRowCounts']
        HostAddress = i['HostAddress']
        SQLText = i['SQLText']
        LockTimes = i['LockTimes']
        ExecutionStartTime = i['ExecutionStartTime']
        ParseRowCounts = i['ParseRowCounts']
        QueryTimes = i['QueryTimes']
        DBName = i['DBName']
        row1 = sheet1.row(j)
        row1.write(0,ReturnRowCounts)
        row1.write(1,HostAddress)
        row1.write(2,SQLText)
        row1.write(3,LockTimes)
        row1.write(4,ExecutionStartTime)
        row1.write(5,ParseRowCounts)
        row1.write(6,QueryTimes)
        row1.write(7,DBName)
        book.save('simple.xls')
        j=j+1
if __name__ == "__main__":
    pagenum=sys.argv[1]
    #dbinstanceid=sys.argv[2]
    res = select_sqlslow(pagenum)
    create_xls(res)

