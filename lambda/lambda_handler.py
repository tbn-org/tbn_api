import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

import base64
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)




def decode_request_context(encoded_string):
    # Replace URL-safe base64 characters with standard base64 characters
    encoded_string = encoded_string.replace('-', '+').replace('_', '/')
    # Add padding to the encoded string if necessary
    padding = '=' * ((4 - len(encoded_string) % 4) % 4)
    decoded_string = base64.b64decode(encoded_string + padding)
    return json.loads(decoded_string)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)



def get_items(event):

    network = None 
    app_name = None 

    
    try:

        network = event.get('queryStringParameters', {}).get('network')
        app_name = event.get('queryStringParameters', {}).get('app_name')

    except:


        if "ctx" in event.get('queryStringParameters'):

            ctx_base64_str = event.get('queryStringParameters', {}).get('ctx')
            ctx_query_params = decode_request_context(ctx_base64_str)

            if "network" in ctx_query_params:
                network = ctx_query_params["network"]


            if "app_name" in ctx_query_params:
                network = ctx_query_params["app_name"]


    if not network:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing query parameter: network'})
        }

    
    response = table.query(
        IndexName="network-index",
        KeyConditionExpression=Key('network').eq(network),
         FilterExpression=Attr('app_name').eq(app_name)

    )
    


    items = response.get('Items', [])

    if not items: 

        response = table.query(
        IndexName="is_default_network-index",
        KeyConditionExpression=Key('is_default_network').eq('true'),
        FilterExpression=Attr('app_name').eq(app_name))


        items = response.get('Items', [])


    
    print(items)

    if items :



            
        return {
            'statusCode': 200,
            'body': json.dumps(items[0]["entry"] , cls=DecimalEncoder)
        }
    else: 
            
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'No Config found'})
        } 
    
        

def handler(event, context):


    if event['httpMethod'] == 'GET':
        return get_items(event)
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

