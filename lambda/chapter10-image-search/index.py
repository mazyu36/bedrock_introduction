import base64
import json
import numpy as np
import cgi
from io import BytesIO
import os
import boto3


modelId = "amazon.titan-embed-image-v1"


embedding_data = []

runtime_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)
s3_client = boto3.client("s3")


# bucket
bucket_name = os.environ["BUCKET_NAME"]


def checkCos(vector1, vector2):
    dot = np.dot(vector1, vector2)
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    similarity = dot / (norm1 * norm2)
    return similarity


def getVec(prompt=None, base64_image_data=None):
    data = {}
    if prompt is not None:
        data["inputText"] = prompt
    if base64_image_data is not None:
        data["inputImage"] = base64_image_data

    body = json.dumps(data)

    response = runtime_client.invoke_model(body=body, modelId=modelId)
    response_body = json.loads(response.get("body").read())
    return response_body["embedding"]


def handler(event, context):

    list_response = s3_client.list_objects_v2(Bucket=bucket_name)

    for obj in list_response["Contents"]:
        file_key = obj["Key"]

        if file_key.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)

            image_data = file_obj["Body"].read()

            base64_image_data = base64.b64encode(image_data).decode()
            image_vec = getVec(base64_image_data=base64_image_data)

            embedding_data.append({"file": file_key, "vector": image_vec})

            print("Processed image:", file_key)

    print("Embedding_data created")

    # マルチパートデータのバイト列を取得
    print(event)
    body = event["body"]
    header = event["headers"]

    fp = BytesIO(base64.b64decode(body))

    environ = {"REQUEST_METHOD": "POST"}
    headers = {
        "content-type": header["content-type"],
        "content-length": header["content-length"],
    }

    fs = cgi.FieldStorage(fp=fp, environ=environ, headers=headers)

    prompt = fs.getvalue("prompt")

    image_data = fs.getvalue("image")
    input_image_base64 = None
    if image_data is not None:
        input_image_base64 = base64.b64encode(image_data).decode()

    input_vec = getVec(prompt=prompt, base64_image_data=input_image_base64)

    cos_data = []

    for item in embedding_data:
        calc = checkCos(input_vec, item["vector"])
        cos_data.append({"value": calc, "file": item["file"]})

    sorted_data = sorted(cos_data, key=lambda x: x["value"], reverse=True)
    key = sorted_data[0]["file"]

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": bucket_name,
            "Key": key,
        },
    )

    result = {"File name": key, "Presigned URL": url}

    return {"statusCode": 200, "body": json.dumps(result, indent=4)}
