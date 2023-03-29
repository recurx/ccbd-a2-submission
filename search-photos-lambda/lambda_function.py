import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import inflect

REGION = 'us-east-1'
HOST = 'search-photos-ga-kqrmxpzyeajdzugfgeypvvkmom.us-east-1.es.amazonaws.com'
INDEX = 'photos'

client = boto3.client('lexv2-runtime')
p = inflect.engine()

def lambda_handler(event, context):
    
    print(event)
    print("Hello there!!!")
    
    msg_from_user = event['queryStringParameters']['q']
    msg_from_user = msg_from_user.replace("%20", " ")
    response = client.recognize_text(
            botId='D6JYXIXIRA', # MODIFY HERE
            botAliasId='B7BT0O0PH1', # MODIFY HERE
            localeId='en_US',
            sessionId="test_user",
            text=msg_from_user)
    msg_from_lex = response.get('messages', [])
    print(response)
    
    label1 = ""
    label2 = ""
    if response["interpretations"][0]["intent"]["slots"]["label1"] != None:
        label1 = response["interpretations"][0]["intent"]["slots"]["label1"]["value"]["interpretedValue"]
    if response["interpretations"][0]["intent"]["slots"]["label2"] != None:
        label2 = response["interpretations"][0]["intent"]["slots"]["label2"]["value"]["interpretedValue"]
    print(label1,label2)
    
    
    if label1 != "":
        label1 = p.singular_noun(label1) if p.singular_noun(label1) else label1
    if label2 != "":
        label2 = p.singular_noun(label2) if p.singular_noun(label2) else label2
    print(label1,label2)
    
    
    opensearch = OpenSearch(hosts=[{
                'host': HOST,
                'port': 443
            }],
            http_auth=get_awsauth(REGION, 'es'),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection)

    query_both = None
    query_label1 = None
    query_label2 = None

    if label2 != "":
        query_both = {
          "query": {
            "bool": {
              "must": [
                { "term": { "labels": label1 }},
                { "term": { "labels": label2 }}
              ]
            }
          }
        }
        query_label2 = {
          "query": {
            "bool": {
              "must": [
                { "term": { "labels": label2}}
              ]
            }
          }
        }

    query_label1 = {
      "query": {
        "bool": {
          "must": [
            { "term": { "labels": label1}}
          ]
        }
      }
    }

    image_list = set()
    if query_both is not None:
        response = opensearch.search(index=INDEX, body=query_both)
        response = response['hits']['hits']

        for response_dict in response:
            image_list.add(response_dict["_id"])

    if len(image_list) < 4:
        response = opensearch.search(index=INDEX, body=query_label1)
        response = response['hits']['hits']

        for response_dict in response:
            image_list.add(response_dict["_id"])

        if query_label2 is not None:
            response = opensearch.search(index=INDEX, body=query_label2)
            response = response['hits']['hits']

            for response_dict in response:
                image_list.add(response_dict["_id"])

    print(list(image_list))
    
    results = {
      'images': list(image_list)
    }

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*'
        },
        'body': json.dumps(results)
    }


def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)