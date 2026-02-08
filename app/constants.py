import os
import boto3
import json
from pprint import pprint
from botocore.exceptions import ClientError


def get_secret():
    secret_name = "my-agent"
    region_name = os.environ.get('AWS_REGION', 'us-east-1')
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        pprint(json.loads(get_secret_value_response['SecretString']))
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    return json.loads(get_secret_value_response['SecretString'])

# def get_secret(secret_name: str, region: str = "us-east-1"):
#     client = boto3.client("secretsmanager", region_name=region)
#     response = client.get_secret_value(SecretId=secret_name)
#     if "SecretString" in response:
#         secret_str = response["SecretString"]
#         return json.loads(secret_str)  # returns dict
#     else:
#         # binary secrets are rare but possible
#         return response["SecretBinary"]
# load key values form aws secrets
agent= get_secret()
OPENAI_API_KEY = agent["OPENAI_API_KEY"]
LANGSMITH_TRACING=agent["LANGSMITH_TRACING"]
LANGSMITH_API_KEY=agent["LANGSMITH_API_KEY"]
LANGSMITH_PROJECT=agent["LANGSMITH_PROJECT"]
PINECONE_API_KEY=agent["PINECONE_API_KEY"]

GPT_EMBEDDING_MODEL="text-embedding-3-small"
INDEX_NAME="medicare-docs"
K=2