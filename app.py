from flask import Flask, request, abort, url_for
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    Emoji,
    VideoMessage,
    AudioMessage,
    LocationMessage,
    StickerMessage,
    ImageMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
import os

app = Flask(__name__)

# 環境變數設置
configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN', ''))
if not configuration.access_token:
    raise ValueError("Missing environment variable: CHANNEL_ACCESS_TOKEN")

line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET', ''))
if not line_handler.channel_secret:
    raise ValueError("Missing environment variable: CHANNEL_SECRET")

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

def get_static_url(filename):
    url = url_for('static', filename=filename, _external=True)
    return url.replace("http", "https")

@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if text == '文字':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="這是文字訊息喔")]
                )
            )
        elif text == '圖片':
            url = get_static_url('Logo.jpg')
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[ImageMessage(original_content_url=url, preview_image_url=url)]
                )
            )
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="我不太明白你的意思，可以試試其他指令，例如：文字、圖片")]
                )
            )

if __name__ == "__main__":
    app.run()
