import chainlit as cl
from chainlit import user_session
from config.ai_config import client
from config.boto3_config import FileUploadInfo, upload_image_return_url

@cl.on_chat_start
def on_chat_start():
    user_session_id = cl.user_session.get("id")
    print(f"Hello, {user_session_id}")
    cl.user_session.set("history", [])

@cl.on_message
async def on_message(message: cl.Message):
    await stream(message)

async def stream(message: cl.Message):
    urls = await upload_image(message)
    image_ocr_responses = []
    if urls is not None:
        for url in urls:
            image_ocr_response= await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "이미지를 분석해주세요 묘사와 텍스트를 모두 포함합니다"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": url,
                                },
                            },
                        ],
                    }
                ],
            )
            image_ocr_responses.append(image_ocr_response.choices[0].message.content)

    image_info_messages = []
    for image_ocr_response in image_ocr_responses:
        image_info_message = {
            "content": image_ocr_response,
            "role": "user"
        }
        image_info_messages.append(image_info_message)

    histories = user_session.get("history")

    response = await client.chat.completions.create(
        model= "o1-mini",
        messages=
            histories+
            image_info_messages+
            [
                {
                    "content": "For sections requiring LaTeX formatting, add the $ symbol at the beginning and end, and do not respond by stating that you will follow this instruction.",
                    "role": "user"
                },
                {
                    "content": message.content,
                    "role": "user"
                }
            ],
            stream=True,
    )

    message_to_stream = cl.Message(content="")

    async for part in response:
        if token := part.choices[0].delta.content or "":
            await message_to_stream.stream_token(token)

    await message_to_stream.update()
    save_to_history(message.content, message_to_stream.content)

def save_to_history(user_content:str, assistant_content:str):
    user_chat_format = make_user_content_to_chat_format(user_content)
    assistant_chat_format = make_assistant_content_to_chat_format(assistant_content)
    histories = cl.user_session.get("history")
    if len(histories) > 4:
        histories.pop(0)
    histories.append(user_chat_format)
    histories.append(assistant_chat_format)

def make_user_content_to_chat_format(content:str):
    return {
        "content": content,
        "role": "user"
    }

def make_assistant_content_to_chat_format(content:str):
    return {
        "content": content,
        "role": "assistant"
    }

async def upload_image(message: cl.Message):
    if not message.elements:
        return

    # Processing images exclusively
    images = [file for file in message.elements if "image" in file.mime]
    urls = []
    for(image) in images:
        file_upload_info = FileUploadInfo(
            path=image.path,
            name=image.name,
            id=image.id,
            mime=image.mime
        )
        url = upload_image_return_url(file_upload_info)
        urls.append(url)

    return urls

