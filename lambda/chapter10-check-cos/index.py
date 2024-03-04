import boto3
import json
import numpy as np

runtime_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)


# model
titan_model_id = "amazon.titan-embed-text-v1"


def checkCos(vector1, vector2):
    dot = np.dot(vector1, vector2)
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    similarity = dot / (norm1 * norm2)
    return similarity


def getVec(prompt):
    body = json.dumps({"inputText": prompt})

    response = runtime_client.invoke_model(body=body, modelId=titan_model_id)

    response_body = json.loads(response.get("body").read())

    return response_body["embedding"]


def handler(event, context):

    body = json.loads(event["body"])
    prompt1 = body["prompt1"]
    prompt2 = body["prompt2"]

    checkCosResult = checkCos(getVec(prompt1), getVec(prompt2))

    response = {"Check cos result": checkCosResult}

    return {"statusCode": 200, "body": json.dumps(response, indent=4)}
