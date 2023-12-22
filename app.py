from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
from keras.models import load_model
import numpy as np
import tensorflow as tf
import requests
from linebot.exceptions import LineBotApiError

app = Flask(__name__)
channel_access_token = os.environ.get('CHANNEL_ACCESS_TOKEN', 'vUK0c7t5wTx/FuYhwUDoNI5AQVjvvlwjPFSR6Rl698i0tf4gzMO9zcvZUx4KPEJHMlDOHMPcLIY2r5OSkByRNZWWHMZzt+78Pxyp38iCL4nX+HwF8jcje70PGtc+Wn4aGUKBBr2WA8EGzdMtJNhIWAdB04t89/1O/w1cDnyilFU=')
line_bot_api = LineBotApi(channel_access_token)
channe_secret = os.environ.get('CHANNEL_SECRET', 'd89ecc5d7744bb60ae98b2f3b487c6f5')
handler = WebhookHandler(channe_secret)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    try:
        message_id = event.message.id
        message_content = line_bot_api.get_message_content(message_id)
        file_path = f"upload/{message_id}.jpg"

        # 儲存照片
        with open(file_path, "wb") as f:
            for chunk in message_content.iter_content():
                f.write(chunk)
        
        # 回傳照片給用戶
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text="這是您的照片！"),
             ImageSendMessage(original_content_url=f"{request.url_root}{file_path}",
                              preview_image_url=f"{request.url_root}{file_path}")]
        )
    except LineBotApiError as e:
        app.logger.error(f"Line Bot API error: {e}")
    except Exception as e:
        app.logger.error(f"Error: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="抱歉，照片處理過程中出現錯誤。")
        )

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
