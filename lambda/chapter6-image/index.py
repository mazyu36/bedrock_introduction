import boto3
import uuid
import json
import os
import base64
import random

runtime_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)

s3_client = boto3.client("s3")


# model
sdxl_model_id = "stability.stable-diffusion-xl-v1"
titan_model_id = "amazon.titan-image-generator-v1"

# bucket
bucket_name = os.environ["BUCKET_NAME"]


def generate_image_sdxl(prompt):
    body = json.dumps(
        {
            "text_prompts": [
                {"text": prompt, "weight": 1.0},
                {
                    "text": "poorly drawn face, poor background details, poorly rendered.",
                    "weight": -1.0,
                },
            ],
            "sample": 1,
            "cfg_scale": 5,
            "seed": random.randint(0, 4294967295),
            "steps": 50,
            "style_preset": "comic-book",
            "clip_guidance_preset": "FAST_GREEN",
            "sampler": "K_DPMPP_2S_ANCESTRAL",
            "height": 512,
            "width": 512,
        }
    )

    response = runtime_client.invoke_model(body=body, modelId=sdxl_model_id)

    response_body = json.loads(response.get("body").read())
    base64_data = response_body.get("artifacts")[0]["base64"]

    return base64_data


def generate_image_titan(prompt):
    body = json.dumps(
        {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": prompt, "negativeText": "poorly drawn face"},
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": "standard",
                "height": 1024,
                "width": 1024,
                "cfgScale": 7.0,
                "seed": random.randint(0, 214783647),
            },
        }
    )

    response = runtime_client.invoke_model(body=body, modelId=titan_model_id)

    response_body = json.loads(response.get("body").read())
    base64_data = response_body.get("images")[0]

    return base64_data


def save_image(base64_data):
    unique_id = str(uuid.uuid4())
    key = f"{unique_id}.png"

    image_data = base64.b64decode(base64_data)

    response = s3_client.put_object(Bucket=bucket_name, Key=key, Body=image_data)

    print("Image saved.")
    print(response)

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": bucket_name,
            "Key": key,
        },
    )

    print("Presigned url created.")

    return url


def handler(event, context):
    body = json.loads(event["body"])
    prompt = body["prompt"]

    base64_data_sdxl = generate_image_sdxl(prompt)
    sdxl_image_url = save_image(base64_data_sdxl)

    body = json.loads(event["body"])
    prompt = body["prompt"]

    base64_data_titan = generate_image_titan(prompt)
    titan_image_url = save_image(base64_data_titan)

    response = {"SDXL Image URL": sdxl_image_url, "Titan Image URL": titan_image_url}

    return {"statusCode": 200, "body": json.dumps(response, indent=4)}
