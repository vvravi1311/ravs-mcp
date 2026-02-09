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

# Use environment variables for local testing, secrets for production
if os.environ.get('AWS_SAM_LOCAL'):
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'test-key')
    LANGSMITH_TRACING = os.environ.get('LANGSMITH_TRACING', 'false')
    LANGSMITH_API_KEY = os.environ.get('LANGSMITH_API_KEY', 'test-key')
    LANGSMITH_PROJECT = os.environ.get('LANGSMITH_PROJECT', 'test')
    PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY', 'test-key')
else:
    agent = get_secret()
    OPENAI_API_KEY = agent["OPENAI_API_KEY"]
    LANGSMITH_TRACING = agent["LANGSMITH_TRACING"]
    LANGSMITH_API_KEY = agent["LANGSMITH_API_KEY"]
    LANGSMITH_PROJECT = agent["LANGSMITH_PROJECT"]
    PINECONE_API_KEY = agent["PINECONE_API_KEY"]

GPT_EMBEDDING_MODEL="text-embedding-3-small"
INDEX_NAME="medicare-docs"
K=2