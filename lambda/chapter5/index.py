import boto3
import json

runtime_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)

# model
titan_model_id = "amazon.titan-text-express-v1"
jurassic_model_id = "ai21.j2-mid-v1"
claude_model_id = "anthropic.claude-v2:1"
claude3_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"


def titan(prompt):
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

    response = runtime_client.invoke_model(body=body, modelId=titan_model_id)

    response_body = json.loads(response.get("body").read())
    output_text = response_body["results"][0]["outputText"]

    return output_text


def jurassic(prompt):
    body = json.dumps(
        {
            "prompt": prompt,
            "maxTokens": 1000,
            "temperature": 0.5,
            "topP": 0.7,
            "stopSequences": [],
            "countPenalty": {"scale": 0},
            "presencePenalty": {"scale": 0},
            "frequencyPenalty": {"scale": 0},
        }
    )

    response = runtime_client.invoke_model(body=body, modelId=jurassic_model_id)

    response_body = json.loads(response.get("body").read())
    question = response_body["prompt"]["text"]
    answer = response_body["completions"][0]["data"]["text"]

    return answer


def claude(prompt):
    body = json.dumps(
        {
            "prompt": f"\n\nHuman:{prompt}\n\nAssistant: ",
            "max_tokens_to_sample": 1000,
            "temperature": 0.5,
            "top_k": 250,
            "top_p": 0.7,
            "stop_sequences": ["\n\nHuman:"],
            "anthropic_version": "bedrock-2023-05-31",
        }
    )

    response = runtime_client.invoke_model(body=body, modelId=claude_model_id)

    response_body = json.loads(response.get("body").read())
    output_text = response_body.get("completion")
    return output_text


def claude3(prompt):
    body = json.dumps(
        {
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": f"{prompt}"}]}
            ],
            "max_tokens": 1000,
            "temperature": 0.5,
            "top_k": 250,
            "top_p": 0.7,
            "anthropic_version": "bedrock-2023-05-31",
        }
    )

    response = runtime_client.invoke_model(body=body, modelId=claude3_model_id)

    response_body = json.loads(response.get("body").read())
    output_text = response_body.get("content")
    return output_text


def handler(event, context):

    body = json.loads(event["body"])
    prompt = body["prompt"]

    # titan
    titan_output = titan(prompt)
    print("# titan output")
    print(titan_output)

    # jurassic
    jurassic_output = jurassic(prompt)
    print("# jurassic output")
    print(jurassic_output)

    # claude
    claude_output = claude(prompt)
    print("# claude output")
    print(claude_output)

    # claude3
    claude3_output = claude3(prompt)
    print("# claude3 output")
    print(claude3_output)

    response_body = {
        "titan": titan_output,
        "jurassic": jurassic_output,
        "claude": claude_output,
        "claude3": claude3_output,
    }

    return {"statusCode": 200, "body": json.dumps(response_body, indent=4)}
