import boto3
import json
import os
import base64
import random
from datetime import datetime

runtime_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)

prompt = "Please sing a song."

# model
titan_model_id = "amazon.titan-text-express-v1"


def handler(event, context):

    body = json.dumps(
        {
            "inputText": prompt,
            "textGenerationConfig": {
                "temperature": 0.5,
                "maxTokenCount": 1000,
                "topP": 0.2,
                "stopSequences": [],
            },
        }
    )

    response = runtime_client.invoke_model_with_response_stream(
        body=body, modelId=titan_model_id
    )

    response_body = response.get("body")

    count = 0
    if response_body:
        for event in response_body:
            chunk = event.get("chunk")
            if chunk:
                chunk_bytes = chunk.get("bytes").decode()
                result = json.loads(chunk_bytes)
                count += 1
                print(f'[{count}]{result["outputText"]}')

    return {"statusCode": 200, "body": "ok"}
