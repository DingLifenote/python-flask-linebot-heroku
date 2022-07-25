from flask import Flask, request, abort
import os
import sys

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

# 從設定好的環境變數，取得LINE要用的的channel_secret和channel_access_token
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

# 確定環境變數有設定好，才允許執行程式
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)


line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# 宣告callback路由，連到LINE的Channel裡面的Webhook
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 收到訊息後，自動回傳訊息
    line_bot_api.reply_message(
        event.reply_token,
        # 回傳訊息的格式為 "自動發言："加上使用者原本的訊息
        TextSendMessage(text="自動發言：" + event.message.text))


if __name__ == "__main__":
    app.run()