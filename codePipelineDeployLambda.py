import json
import boto3

def lambda_handler(event, context):
    
    lambda_client = boto3.client('lambda')
    s3_client = boto3.client('s3')

    #Lambda to update index-photots
    s3_bucket_name = 'lambdas-ccbd-a2'
    s3_object_key = 'index-photos.zip'
    response = s3_client.get_object(Bucket=s3_bucket_name, Key=s3_object_key)
    zip_content = response['Body'].read()
    lambda_function_name = 'index-photos-ga'
    response = lambda_client.update_function_code(
        FunctionName=lambda_function_name,
        ZipFile=zip_content
    )
    print(response)
    
    #Lambda to update search-photots
    s3_bucket_name = 'lambdas-ccbd-a2'
    s3_object_key = 'search-photos.zip'
    response = s3_client.get_object(Bucket=s3_bucket_name, Key=s3_object_key)
    zip_content = response['Body'].read()
    lambda_function_name = 'search-photos-ga'
    response = lambda_client.update_function_code(
        FunctionName=lambda_function_name,
        ZipFile=zip_content
    )
    print(response)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Lambda Updated!')
    }
