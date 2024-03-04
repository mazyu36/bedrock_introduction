import boto3
import json

bedrock_client = boto3.client(service_name="bedrock", region_name="us-east-1")


def handler(event, context):
    body = json.loads(event["body"])

    provider = body.get("provider", None)
    mode = body.get("mode", None)  # TEXT, IMAGE or EMBEDDING

    if provider is not None and mode is not None:
        list_result = bedrock_client.list_foundation_models(
            byProvider=provider, byOutputModality=mode
        )
    elif provider is not None:
        list_result = bedrock_client.list_foundation_models(byProvider=provider)
    elif mode is not None:
        list_result = bedrock_client.list_foundation_models(byOutputModality=mode)
    else:
        list_result = None

    if list_result is None:
        response = {"result": "Not found"}
    else:
        model_list = list_result.get("modelSummaries")
        response = []
        for item in model_list:
            response.append(
                {
                    "modelName": item["modelName"],
                    "modelId": item["modelId"],
                    "inputModalities": item["inputModalities"],
                    "outputModalities": item["outputModalities"],
                }
            )

    return {"statusCode": 200, "body": json.dumps(response, indent=4)}
