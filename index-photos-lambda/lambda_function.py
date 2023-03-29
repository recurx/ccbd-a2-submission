import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from datetime import datetime
import inflect

REGION = 'us-east-1'
HOST = 'search-photos-ga-kqrmxpzyeajdzugfgeypvvkmom.us-east-1.es.amazonaws.com'
INDEX = 'photos'

s3 = boto3.client('s3')
p = inflect.engine()

def lambda_handler(event, context):
    print(event)
    print("Hello there!!!")
    s3_bucket = 'ccbd-b2-photos-ga'
    s3_key = event['Records'][0]['s3']['object']['key']
    object_metadata = s3.head_object(Bucket=s3_bucket, Key=s3_key)
    labels_list = []
    print("Object Metadata",object_metadata)
    if 'customlabels' in object_metadata['Metadata']:
        custom_labels = object_metadata['Metadata']['customlabels']
        labels_list = custom_labels.split(',')
        print("Custom Labels", labels_list)
    rekognition = boto3.client('rekognition')
    response = rekognition.detect_labels(
        Image={
            'S3Object': {
                'Bucket': s3_bucket,
                'Name': s3_key
            }
        }, 
        MinConfidence=70
    )
    # print(response)
    for label in response['Labels']:
        labels_list.append(label['Name'])
    print(labels_list)

    singular_labels = []
    for label in labels_list:
        if p.singular_noun(label) != False:
            singular_labels.append(p.singular_noun(label))
        else:
            singular_labels.append(label)
    print(singular_labels)

    client = OpenSearch(hosts=[{
                'host': HOST,
                'port': 443
            }],
            http_auth=get_awsauth(REGION, 'es'),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection)
    
    # Define the JSON object to be put into OpenSearch
    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    json_obj = {
        "objectKey": s3_key,
        "bucket": s3_bucket,
        "createdTimestamp": current_time,
        "labels": singular_labels
    }
    # Convert the JSON object to a string
    json_str = json.dumps(json_obj)
    # Put the JSON object into OpenSearch
    client.index(index=INDEX, id=s3_key, body=json_str)
    res = client.get(index=INDEX, id=s3_key)
    print(res)
    

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)