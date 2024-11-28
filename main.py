import chainlit as cl
from config.ai_config import client
from config.boto3_config import FileUploadInfo, upload_image_return_url

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

    response = await client.chat.completions.create(
        model= "o1-mini",
        messages=image_info_messages+[
            {
                "content": message.content+ "수학 기호를 출력하는 경우 앞 뒤에 $ 기호를 사용하세요.",
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

async def upload_image(message: cl.Message):
    if not message.elements:
        return

    # Processing images exclusively
    images = [file for file in message.elements if "image" in file.mime]
    urls = []
    for(image) in images:
        print(image)
        file_upload_info = FileUploadInfo(
            path=image.path,
            name=image.name,
            id=image.id,
            mime=image.mime
        )
        url = upload_image_return_url(file_upload_info)
        urls.append(url)

    return urls

