import json
import requests
import os
import boto3
from parse import *

""" Cloud API asynchronous "PDF To Text" job example.
    Allows to avoid timeout errors when processing huge or scanned PDF documents.
"""
        
def lambda_handler(event, context):
    # TODO implement
     # Python program to read
    # json file
    parse_json()
    # Opening JSON file
    f = open('/tmp/result.json')
    notInclude=['Start', 'End', 'Dispostion', 'General Location', 'Case Number', 'Date/Time','20-St-rt::']
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    # Iterating through the json
    # list
    rowCount=0;
    dict={}
    isNewCase=False
    occurDateTime=''
    offense=""
    location=""
    #dateTimePattern=some regex
    for onePage in data['document']['page']:
        for row in onePage['row']:
            columnCounter=0
            for column in row['column']:   
                if(len(column['text'])>0):
                    if(rowCount==0 and columnCounter==0):
                        dict['campus']=column['text']['#text']
                    if(rowCount==0 and columnCounter==6):
                        updateDate=column['text']['#text'].replace("Printed on ", "")
                        dict['last-updated']=updateDate
                    if('2022' in column['text']['#text'] and rowCount>1):
                        isNewCase=True
                        offense=offense.replace('_'," ")
                        booleanCount=0;
                        for i in notInclude:
                            if (i in offense or i in occurDateTime):
                                booleanCount+=1
                        if(booleanCount==0):
                            occurDateTime = FormatDate(occurDateTime)
                            dict[occurDateTime]=offense+location
                        offense=""
                    else:
                        isNewCase=False
                    #get the key
                    if(isNewCase==False and columnCounter==2 and 'Date/Time Occurred' not in column['text']['#text']):
                        occurDateTime=column['text']['#text']
                    #get the value (offense and location)
                    if(isNewCase==False and columnCounter==4):
                        offense+=column['text']['#text']+ " "
                    if(isNewCase==False and columnCounter==5):
                        location="location is "+column['text']['#text']+" "
                if(len(column['text'])==0 and columnCounter==0):
                    if(isNewCase==False and columnCounter==4):
                        offense+=column['text']['#text']
                columnCounter+=1
            rowCount+=1
    print("Going to firstSeven")
    firstSeven={A:N for (A,N) in [x for x in dict.items()][:7]}
    print(firstSeven)
    # Closing file
    f.close()
    
    
    dynamodb = boto3.resource('dynamodb').Table('CrimeInfo')
    CrimeID = 0
    for x in firstSeven:
        dynamodb.put_item(
            Item={
                'CrimeID' : CrimeID,
                'Date' : x,
                'Crime' : firstSeven[x]
            })
        CrimeID+=1
   
    return {
        'statusCode': 200,
        'body': str(dict)
    }

def FormatDate(Date):
    Month = Date[0:2]
    Day = Date[3:5]
    Year = "20"+Date[6:8]
    Hour = Date[9:11]
    Minute = Date[12:14]
    FormattedDate = Year+"-"+Month+"-"+Day+":"+Hour+":"+Minute
    return FormattedDate
    