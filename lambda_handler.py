import json
import base64
import traceback
from app.rag_tools import retrieve_context

def handler(event, context):
    req_id = None
    try:
        # Handle OPTIONS for CORS
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, x-api-key'
                },
                'body': json.dumps({})
            }

        # Ensure request is from API Gateway
        request_context = event.get('requestContext')
        if not request_context or 'apiId' not in request_context:
            return {
                "statusCode": 403,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Direct invocation not allowed"})
            }

        # Validate API Key
        headers = event.get('headers', {})
        headers_lower = {k.lower(): v for k, v in headers.items()}
        api_key = headers_lower.get("x-api-key")
        if not api_key:
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "API key required"})
            }

        # Parse MCP request
        body = event.get('body', '{}')
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body).decode('utf-8')

        request = json.loads(body)
        method = request.get('method')
        req_id = request.get('id')

        # MCP: initialize
        if method == 'initialize':
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "ravs-mcp",
                        "version": "0.1.0"
                    }
                }
            }
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(response)
            }

        # MCP: tools/list
        if method == 'tools/list':
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [{
                        "name": "retrieve_documents",
                        "description": "Retrieve relevant documentation to help answer Insurance agents queries about Real-Time clause and Benefit lookup",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"}
                            },
                            "required": ["query"]
                        }
                    }]
                }
            }

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(response)
            }

        # MCP: tools/call
        elif method == 'tools/call':
            params = request.get('params', {})
            tool_name = params.get('name')
            arguments = params.get('arguments', {})

            print("***********************************************************   in tool calls   **********************")
            if tool_name == 'retrieve_documents':
                import time
                start = time.time()
                print("***********************************************************   in retrieve_documents   **********")
                serialized, docs = retrieve_context(arguments['query'])
                print(f"*** retrieve_context took {time.time() - start:.2f}s ***")
                print("***********************************************************   docs retreived   **********")
                
                docs_dict = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]
                
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": serialized},
                            {"type": "text", "text": json.dumps(docs_dict, indent=2)}
                        ]
                    }
                }

                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps(response)
                }

        # Unsupported method
        error_response = {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": "Unsupported method"}
        }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(error_response)
        }

    except Exception as e:
        error_response = {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32001,
                "message": str(e),
                "data": traceback.format_exc()
            }
        }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(error_response)
        }
