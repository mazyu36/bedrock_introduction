import json
from langchain_community.llms import Bedrock
from langchain_community.chat_models import BedrockChat

from langchain.schema import HumanMessage, SystemMessage

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from langchain.prompts import PromptTemplate, ChatPromptTemplate


# model
titan_model_id = "amazon.titan-text-express-v1"
jurassic_model_id = "ai21.j2-mid-v1"
claude_model_id = "anthropic.claude-v2:1"


llm = Bedrock(model_id=titan_model_id)


chat = BedrockChat(model_id=claude_model_id)

conversation = ConversationChain(
    llm=llm, verbose=False, memory=ConversationBufferMemory()
)


def generate(prompt):
    result = llm.generate(
        [f"Please answer about {prompt} within 20 words."],
        {
            "temperature": 0.7,
            "maxTokens": 300,
            "topP": 1,
        },
    )
    return result.generations[0][0].text.strip()


def invoke_chat(prompt):
    messages = [
        SystemMessage(content=f"Please answer about {prompt} within 20 words."),
        HumanMessage(content=prompt),
    ]

    response = chat(messages, temperature=0.7, top_k=250, top_p=1)

    return response.content


def invoke_conversation(prompt):
    response = conversation.predict(input=prompt)

    return response


def use_template(person_name):
    template_prompt = PromptTemplate.from_template(
        "Please answer about {person_name} within 20 words."
    )

    runnable = template_prompt | llm

    response = runnable.invoke({"person_name": person_name})

    return response


def use_chat_template(person_name):
    template_prompt = ChatPromptTemplate.from_template(
        "「{person_name}について教えて」"
    )

    chain = template_prompt | chat

    response = chain.invoke({"person_name": person_name})

    return response.content.strip()


def handler(event, context):
    body = json.loads(event["body"])
    prompt = body["prompt"]

    # Generate
    generate_output = generate(prompt)

    # Chat
    chat_output = invoke_chat(prompt)

    # Conversation
    conversation_output = invoke_conversation(prompt)

    # Template
    template_output = use_template(prompt)

    # Chat Template
    chat_template_output = use_chat_template(prompt)

    # 結果をまとめる
    response = {
        "generate_output": generate_output,
        "chat_output": chat_output,
        "conversation_output": conversation_output,
        "template_output": template_output,
        "chat_template_output": chat_template_output,
    }

    return {
        "statusCode": 200,
        "body": json.dumps(response, ensure_ascii=False, indent=4),
    }
