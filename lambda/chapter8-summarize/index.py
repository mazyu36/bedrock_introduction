import boto3
import json

from langchain_community.chat_models import BedrockChat

from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

s3_client = boto3.client("s3")

# model
# claude_model_id = "anthropic.claude-v2:1"
# claude_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
claude_model_id = "anthropic.claude-3-haiku-20240307-v1:0"


chat = BedrockChat(model_id=claude_model_id)


template_prompt = ChatPromptTemplate.from_template(
    """以下のテキストを日本語で要約しなさい:

    {content}

    要約:"""
)


# preprocessing
def get_3lines(content):
    lines = content.split(".")
    return {"content": "".join(lines[:3])}


# postprocessing
def joinLines(msg):
    return msg.content.replace("\n", " ")


def handler(event, context):

    print("Received event: " + json.dumps(event, indent=2))

    # POSTで送られてきたテキストファイルの内容を取得
    if "body" in event:
        file_content = event["body"]
    else:
        print("No body found in the event.")
        return {
            "statusCode": 400,
            "body": json.dumps("No file content found in the request body."),
        }

    runnable = (
        RunnableLambda(get_3lines) | template_prompt | chat | RunnableLambda(joinLines)
    )

    summary = runnable.invoke(file_content)

    response = {"result": summary}

    return {
        "statusCode": 200,
        "body": json.dumps(response, ensure_ascii=False, indent=4),
    }
