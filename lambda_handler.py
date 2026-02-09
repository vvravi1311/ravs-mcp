import json
import base64

def handler(event, context):
    """Lambda handler for MCP server via API Gateway"""
    try:
        # Ensure request is from API Gateway
        request_context = event.get('requestContext')
        if not request_context or 'apiId' not in request_context:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Direct invocation not allowed'})
            }

        # Validate API Key
        api_key = event.get('headers', {}).get('x-api-key')
        if not api_key:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'API key required'})
            }

        # Parse MCP request from API Gateway
        body = event.get('body', '{}')
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body).decode('utf-8')

        request = json.loads(body)
        method = request.get('method')

        # Handle MCP protocol methods
        if method == 'tools/list':
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'tools': [{
                        'name': 'retrieve_documents',
                        'description': 'Retrieve relevant documentation to help answer answers Insurance agents\' queries about Real-Time clause and Benefit lookup',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'query': {'type': 'string'}
                            },
                            'required': ['query']
                        }
                    }]
                })
            }

        elif method == 'tools/call':
            params = request.get('params', {})
            tool_name = params.get('name')
            arguments = params.get('arguments', {})

            if tool_name == 'retrieve_documents':
                from app.rag_tools import retrieve_context
                serialized, docs = retrieve_context(arguments['query'])
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'content': [{'type': 'text', 'text': serialized}]
                    })
                }

        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Unsupported method'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
