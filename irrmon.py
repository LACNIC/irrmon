#!/usr/bin/env python3

import json
import logging
import shlex
import subprocess
from datetime import datetime
import time
import prometheus_client as prom
import filecmp
import os

irrBaseDir = '/usr/src/irrmon/data'
#irrBaseDir = './data'
whoisToProme = {}
irrDict = {}

#db_irr_sources = {"RADB": "whois.radb.net","LACNIC": "irr.lacnic.net"} 

irrd_query_style = {"aut-num": "!maut-num,", "mntner": "!mmntner,", "source": "!s", "as-set": "!mas-set,"} 
ripe_query_style = {"aut-num": "-T aut-num", "mntner": "-T mntner", "source": "!s", "as-set": "-T as-set"} 
   
response_codes = {"D": 0, "A": 1, "N": 2, "T": 3, "F": 4}

def read_irr_json(fileName):
    with open(fileName, encoding='utf-8') as f:
        data = json.load(f)
    f.close()
    return data 

    

def get_irr_object(irrSource, irrSourceWhois, irrStyle, queryObjectType, queryObject, queryTimeout): 
    if irrStyle == 'irrd':
        queryCommand = irrd_query_style[queryObjectType]
        zz = "whois -h " + irrSourceWhois + " '" + queryCommand + queryObject + "'"
    elif irrStyle == 'ripe':
        queryCommand = ripe_query_style[queryObjectType] 
        zz = "whois -h " + irrSourceWhois + " " + queryCommand + " " + queryObject
    else:
        notStyle="Not style defined for " + irrSource 
        print(notStyle)
        logging.error(notStyle)
        return False, "notStyle" 
    
    print(irrStyle) 
    logging.info(irrSource + ": style=" + irrStyle) 
   
    try:
        stat = subprocess.run(shlex.split(zz), capture_output=True, timeout=int(queryTimeout))
    except subprocess.TimeoutExpired:
        timeOut = "Timeout whois source: " + irrSource + ': ' + irrSourceWhois
        print(timeOut) 
        logging.error(timeOut)
        if irrSource not in whoisToProme: 
            whoisToProme[irrSource] = 'T'
            logging.info(irrSource + ": T")
        return False, "Timeout" 

    if stat.returncode == 0:
        return True, stat.stdout
    else:
        print("Empty response from IRR")
        logging.info("Empty response from IRR")
        if irrSource not in whoisToProme: 
            whoisToProme[irrSource] = 'N'
            logging.info(irrSource + ": N")
        return False, stat.returncode 

#
# For a successful response returning data, the response is:
# A<length>
# <response content>
# C
#
# The length is the number of bytes in the response, including the newline immediately after the response content. Different objects are part of one lock of response content, each object separated by a blank line.
# 
# If the query was valid, but no entries were found, the response is:
# C
#
# If the query was valid, but the primary key queried for did not exist:
# D
#
# If the query was invalid:
# F <error message>
#

def query_process(irrName, query, queryObjectType, queryObject):
    global whoisToProme
    jsonOut = {}
    lineInQuery = len(query.strip().decode().splitlines())
    for line in query.strip().decode().splitlines():
        if line.startswith('D'):
            print("The primary key queried not exist")
            logging.info(irrName + ": The primary key queried not exist")
            if irrName not in whoisToProme: 
                whoisToProme[irrName] = 'D'
                logging.info(irrName + ": D")
            break
        if line.startswith('A'):
            if irrName not in whoisToProme: 
                whoisToProme[irrName] = 'A'
                logging.info(irrName + ": A")
            continue
        if line.startswith('C') and lineInQuery >= 2:
            continue
        if line.startswith('%ERROR:101: no entries found'):
            print('%ERROR:101: no entries found')
            logging.info(irrName + ": %ERROR:101: no entries found")
            if irrName not in whoisToProme: 
                whoisToProme[irrName] = 'D'
                logging.info(irrName + ": D")
            continue
        if line.startswith('%'):
            continue
        if line.startswith('Found a referral to'):
            break
        if len(line) == 0:
            continue
        if line.startswith(queryObjectType + ":"):
            if irrName not in whoisToProme: 
                whoisToProme[irrName] = 'A'
                logging.info(irrName + ": A")
        print(line)
        #logging.info(line)
        key, value = line.strip().split(None, 1)
        jsonOut[key] = value

    f = open(irrBaseDir + '/html/objects/' + irrName + '.json', "w")
    f.write(json.dumps(jsonOut, indent=4))
    f.write("\n")
    f.close()
    return jsonOut     

def prometheus_metric(queryObjectType, queryObject, querySourceIRR):
    global irrDict
    now = datetime.now()
    ts = int(datetime.timestamp(now))
    irrDict['timestamp'] = ts
    irrDict['date'] = now.strftime("%Y/%m/%d %H:%M:%S") 
    irrDict['querySourceIRR'] = querySourceIRR
    irrDict['queryObjectType'] = queryObjectType
    irrDict['queryObject'] = queryObject
    irrDict['irr'] = whoisToProme 
    jsonOut = json.dumps(irrDict, indent=4)
    f = open(irrBaseDir + '/html/log/irr_metrics.json', "a")
    f.write(jsonOut)
    f.write("\n")
    f.close()

def create_log_file(myLogFile):
    logging.basicConfig(filename=myLogFile, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.DEBUG)

def prometheus_conf():
    for coll in list(prom.REGISTRY._collector_to_names.keys()):
        prom.REGISTRY.unregister(coll)

# mntner:        MNT-PAL-COLO
# descr:         LACNIC - Latin American and Caribbean IP address
# auth:          NONE
# upd-to:        iippadmin@lacnic.net
# admin-c:       AIL
# tech-c:        AIL
# remarks:       Timestamp 2022-10-04T14:52:26Z
# mnt-by:        MNT-PAL-COLO
# changed:       iippadmin@lacnic.net 20221004 
# source:        LACNIC

def mnt_pal_colo(key, query, queryObjectType, queryObject):
#    zz = query.strip().decode().splitlines():
#    if  
    for line in query.strip().decode().splitlines():
        print(line)
        logging.info(line)

def check_file_diff(querySourceIRR):
    global whoisToProme
    fileIRR = irrBaseDir + '/html/objects/' + querySourceIRR + '.json' 
    print("-----------------")
    for i,j in whoisToProme.items():
        print(i,j)
        if (j =='D' or j == 'T' or j == 'N'):
            continue
        if i != querySourceIRR:
            f2 = irrBaseDir + '/html/objects/' + i + '.json' 
            #print(fileIRR,f2)
            filecmp.clear_cache()
            if filecmp.cmp(fileIRR, f2):
                continue
            else:
                whoisToProme[i] = "F"
                logging.info(i + ": F, Differences in object from " + querySourceIRR)
            print(i, whoisToProme[i])
        
if __name__ == '__main__':
   
    myLogFile = irrBaseDir + '/html/log/irr_check.log'
    create_log_file(myLogFile)

    prometheus_conf()
    prom.start_http_server(8000)

    RESPONSE_IRR_QOS = prom.Gauge('irr_query_object_source', 'Query object IRR source', ["querySourceIRR"])
    RESPONSE_IRR_QOT = prom.Gauge('irr_query_object_type', 'Query object type', ["queryObjectType"])
    RESPONSE_IRR_QOB = prom.Gauge('irr_query_object', 'Query object', ["queryObject"])
    RESPONSE_IRR_QIN = prom.Gauge('irr_query_interval', 'Queries interval in seconds', ["queryInterval"])
    RESPONSE_IRR_QTO = prom.Gauge('irr_query_timeout', 'Timeout response in seconds', ["queryTimeout"])
        
    RESPONSE_IRR_GAUGE = prom.Gauge('irr_query_object_found', 'IRR object query result: not found (0), found (1), empty response (2), timeout (3)', ["irr", "response"])
    RESPONSE_IRR_COUNT = prom.Counter('irr_number_of_queries_cycles', 'Number of queries cycles to all the Registries') 
   

    while True:
        
        irrInput = read_irr_json(irrBaseDir + '/html/input/irr_input.json')
     
        while any([irrInput[keys] in ("", [], None, 0, False) for keys in irrInput]):
            logging.info("Input: " + str(irrInput))
            time.sleep(30)
            irrInput = read_irr_json(irrBaseDir + '/html/input/irr_input.json')

        querySourceIRR = irrInput['querySourceIRR']
        queryObjectType = irrInput['queryObjectType']
        queryObject = irrInput['queryObject']
        queryInterval = irrInput['queryInterval']
        queryTimeout = irrInput['queryTimeout']
        queryMirrorsList = irrInput['queryMirrorsList']
       
        print(str(irrInput))
        logging.info("Input: " + str(irrInput))

        irrSourcesDB = read_irr_json(irrBaseDir + '/html/input/irr_whois_list.json')
        whoisToProme.clear()
        for key,value in irrSourcesDB['source'].items():
            result = False
            if value['status'] == 'down': continue
            if key == querySourceIRR:
                print("-----------------") 
                print(key)
                result, query = get_irr_object(key, value['whois'], value['style'], queryObjectType, queryObject, queryTimeout)
            if value['status'] == 'rir' and key != querySourceIRR:
                if isinstance(value['mirrored'], list):
                    if querySourceIRR in value['mirrored']:
                        print("-----------------")
                        print(key)
                        result, query = get_irr_object(key, value['whois'], value['style'], queryObjectType, queryObject, queryTimeout)
                    else:
                        continue
                else:
                    continue
            if value['status'] == 'up' and (key in queryMirrorsList):
                print("-----------------") 
                print(key)
                result, query = get_irr_object(key, value['whois'], value['style'], queryObjectType, queryObject, queryTimeout)
            if result:
                query_process(key, query, queryObjectType, queryObject)
#               mnt_pal_colo(key, query, queryObjectType, queryObject)
    
        check_file_diff(querySourceIRR)

        irrDict.clear() 
        prometheus_metric(queryObjectType, queryObject, querySourceIRR)
     
        RESPONSE_IRR_QOS.clear()
        RESPONSE_IRR_QOS.labels(querySourceIRR=querySourceIRR).set(1)
        RESPONSE_IRR_QOT.clear()
        RESPONSE_IRR_QOT.labels(queryObjectType=queryObjectType).set(1)
        RESPONSE_IRR_QOB.clear()
        RESPONSE_IRR_QOB.labels(queryObject=queryObject).set(1)
        RESPONSE_IRR_QIN.clear()
        RESPONSE_IRR_QIN.labels(queryInterval=queryInterval).set(1)
        RESPONSE_IRR_QTO.clear()
        RESPONSE_IRR_QTO.labels(queryTimeout=queryTimeout).set(1)
        RESPONSE_IRR_GAUGE.clear()
        
        for key,value in irrDict['irr'].items():
            RESPONSE_IRR_GAUGE.labels(irr=key,response=value).set(response_codes[value])
    
        RESPONSE_IRR_COUNT.inc()

        time.sleep(int(queryInterval))
      
