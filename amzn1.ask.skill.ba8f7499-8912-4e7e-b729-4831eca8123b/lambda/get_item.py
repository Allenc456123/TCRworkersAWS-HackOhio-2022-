import boto3


def get_item():
    table = boto3.resource('dynamodb').Table('Crime_Info')
    item = table.get_item(
        Key = {
            'CaseNumber' : '1'
            'Date' : 'TEST'
        })
    item = item['Item']
    return item