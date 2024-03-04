import json
import numpy as np
import boto3

data = [
    "Macintosh. Apple computer. Beautiful design. Easy to use interface. very expensive. Not compatible with other computers. Suitable for creative work.",
    "Windows machine. A computer running Microsoft's OS. A wide range of lineups from low to high prices. Huge amount of software. Full range of peripheral equipment. It has an overwhelming market share in business use.",
    "Linux machine. Equipped with open source OS. Very few products are sold. There is little information and you have to solve every problem on your own. Used in the field of development and research.",
    "Chromebook. Low cost computers by Google. Minimum hardware required. It is designed with the premise that much of the work will be done in the cloud. Widely used in the educational field.",
    "Android. It is equipped with an OS developed by Google. It is used in smartphones and tablets, and there are also small PCs. Touch panel operation. It is often used as a second machine.",
]

modelId = "amazon.titan-embed-text-v1"

embedding_data = []

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


def getVec(p):
    body = json.dumps({"inputText": p})
    response = runtime_client.invoke_model(body=body, modelId=modelId)
    response_body = json.loads(response.get("body").read())
    return response_body["embedding"]


def handler(event, context):

    body = json.loads(event["body"])
    prompt = body["prompt"]

    embedded_prompt = getVec(prompt)

    for item in data:
        vector = getVec(item)
        embedding_data.append({"content": item, "embedded": vector})

    cos_data = []

    for item in embedding_data:
        calc = checkCos(embedded_prompt, item["embedded"])
        cos_data.append({"value": calc, "content": item["content"]})

    sorted_data = sorted(cos_data, key=lambda x: x["value"], reverse=True)

    response = {"prompt": prompt, "result": sorted_data[0]["content"]}

    return {"statusCode": 200, "body": json.dumps(response, indent=4)}
