# AWS Deployment Steps

## Prerequisites
- AWS CLI configured with credentials
- Docker Desktop running
- AWS Secrets Manager secret named "my-agent" with keys:
  - OPENAI_API_KEY
  - PINECONE_API_KEY
  - LANGSMITH_API_KEY (optional)
  - LANGSMITH_TRACING (optional)
  - LANGSMITH_PROJECT (optional)

## Deployment Steps

### 1. Build the Lambda function
```bash
sam build --use-container
```

### 2. Deploy to AWS (first time)
```bash
sam deploy --guided
```

You'll be prompted for:
- **Stack Name**: `mcp-server-stack` (or your choice)
- **AWS Region**: `us-east-1` (or your choice)
- **Parameter SecretName**: `my-agent` (default)
- **Confirm changes before deploy**: Y
- **Allow SAM CLI IAM role creation**: Y
- **Disable rollback**: N
- **MCPServerFunction has no authentication**: N (API key required)
- **Save arguments to configuration file**: Y

### 3. Get the API endpoint
After deployment completes, look for:
```
Outputs
Key                 MCPApi
Value               https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/Prod/mcp

Key                 MCPApiKeyId
Value               abc123xyz
```

### 4. Get the API Key value
```bash
aws apigateway get-api-key --api-key <MCPApiKeyId> --include-value --query 'value' --output text
```

### 5. Test the deployed endpoint
```bash
curl -X POST https://YOUR_API_ENDPOINT/Prod/mcp \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

## Subsequent Deployments

```bash
sam build --use-container
sam deploy
```

## Delete Stack

```bash
sam delete
```

## Security Features
- API Key authentication required
- Rate limiting: 100 requests/second
- Burst limit: 200 requests
- Secrets stored in AWS Secrets Manager
