import boto3
import json
import os
import base64
import cgi
from io import BytesIO
import uuid

runtime_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)

s3_client = boto3.client("s3")

# model
sdxl_model_id = "stability.stable-diffusion-xl-v1"

# bucket
bucket_name = os.environ["BUCKET_NAME"]


def edit_image_sdxl(prompt, input_image_base64, mask_image_base64):
    body = json.dumps(
        {
            "text_prompts": [
                {"text": prompt},
            ],
            "init_image_mode": "IMAGE_STRENGTH",
            "image_strength": 0.35,
            "init_image": input_image_base64,
            "mask_source": "MASK_IMAGE_WHITE",
            "mask_image": mask_image_base64,
            "cfg_scale": 7,
            "clip_guidance_preset": "FAST_BLUE",
            "sampler": "K_DPM_2_ANCESTRAL",
            "samples": 1,
            "steps": 30,
        }
    )

    response = runtime_client.invoke_model(body=body, modelId=sdxl_model_id)

    response_body = json.loads(response.get("body").read())
    output_image_base64 = response_body.get("artifacts")[0]["base64"]

    return output_image_base64


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
    # マルチパートデータのバイト列を取得
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
    input_image_base64 = base64.b64encode(image_data).decode()

    mask_image_data = fs.getvalue("mask_image")
    mask_image_base64 = base64.b64encode(mask_image_data).decode()

    output_image_base64_sdxl = edit_image_sdxl(
        prompt, input_image_base64, mask_image_base64
    )

    url = save_image(output_image_base64_sdxl)

    response = {"SDXL edited image URL": url}

    return {"statusCode": 200, "body": json.dumps(response, indent=4)}
