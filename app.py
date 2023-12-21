from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
from keras.models import load_model
import numpy as np
import tensorflow as tf
import requests

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
    #message = TextSendMessage(text=event.message.text)
    #line_bot_api.reply_message(event.reply_token, message)
    try:
        # 獲取圖片
        message_content = line_bot_api.get_message_content(event.message.id)
        
        # 儲存圖片
        with open("user_image.jpg", "wb") as f:
            for chunk in message_content.iter_content():
                f.write(chunk)
        test_image = process_image("user_image.jpg")
        newtest_image = np.expand_dims(test_image, axis=0)
        file_id = '1g_8yo2_gRBdzibwwF6uPZ-v8fvwzrZ0t'
        destination = 'model.h5'
        download_file_from_google_drive(file_id, destination)
        model = load_model('model.h5')
        predictions = model.predict(newtest_image)
        predicted_result = predict_breed(predictions)
        reply_message = TextSendMessage(text=str(predicted_result))
        line_bot_api.reply_message(event.reply_token, reply_message)
    except LineBotApiError as e:
        # 錯誤處理
        return 'error'
def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()
    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)   

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def process_image(image_path, img_size=224):
  # Read in an image file
  image = tf.io.read_file(image_path)
  # Turn the jpeg image into numerical Tensor with 3 colour channels (Red, Green, Blue)
  image = tf.image.decode_jpeg(image, channels=3)
  # Convert the colour channel values from 0-255 to 0-1 values
  image = tf.image.convert_image_dtype(image, tf.float32)
  # Resize the image to our desired value (224, 224)
  image = tf.image.resize(image, size=[IMG_SIZE, IMG_SIZE])

  return image

def predict_breed(predictions):
    dog_breeds = [
    'affenpinscher', 'afghan_hound', 'african_hunting_dog', 'airedale',
    'american_staffordshire_terrier', 'appenzeller', 'australian_terrier',
    'basenji', 'basset', 'beagle', 'bedlington_terrier', 'bernese_mountain_dog',
    'black-and-tan_coonhound', 'blenheim_spaniel', 'bloodhound', 'bluetick',
    'border_collie', 'border_terrier', 'borzoi', 'boston_bull',
    'bouvier_des_flandres', 'boxer', 'brabancon_griffon', 'briard',
    'brittany_spaniel', 'bull_mastiff', 'cairn', 'cardigan',
    'chesapeake_bay_retriever', 'chihuahua', 'chow', 'clumber', 'cocker_spaniel',
    'collie', 'curly-coated_retriever', 'dandie_dinmont', 'dhole', 'dingo',
    'doberman', 'english_foxhound', 'english_setter', 'english_springer',
    'entlebucher', 'eskimo_dog', 'flat-coated_retriever', 'french_bulldog',
    'german_shepherd', 'german_short-haired_pointer', 'giant_schnauzer',
    'golden_retriever', 'gordon_setter', 'great_dane', 'great_pyrenees',
    'greater_swiss_mountain_dog', 'groenendael', 'ibizan_hound', 'irish_setter',
    'irish_terrier', 'irish_water_spaniel', 'irish_wolfhound',
    'italian_greyhound', 'japanese_spaniel', 'keeshond', 'kelpie',
    'kerry_blue_terrier', 'komondor', 'kuvasz', 'labrador_retriever',
    'lakeland_terrier', 'leonberg', 'lhasa', 'malamute', 'malinois', 'maltese_dog',
    'mexican_hairless', 'miniature_pinscher', 'miniature_poodle',
    'miniature_schnauzer', 'newfoundland', 'norfolk_terrier',
    'norwegian_elkhound', 'norwich_terrier', 'old_english_sheepdog',
    'otterhound', 'papillon', 'pekinese', 'pembroke', 'pomeranian', 'pug',
    'redbone', 'rhodesian_ridgeback', 'rottweiler', 'saint_bernard', 'saluki',
    'samoyed', 'schipperke', 'scotch_terrier', 'scottish_deerhound',
    'sealyham_terrier', 'shetland_sheepdog', 'shiba', 'shih-tzu',
    'siberian_husky', 'silky_terrier', 'soft-coated_wheaten_terrier',
    'staffordshire_bullterrier', 'standard_poodle', 'standard_schnauzer',
    'sussex_spaniel', 'tibetan_mastiff', 'tibetan_terrier', 'toy_poodle',
    'toy_terrier', 'vizsla', 'walker_hound', 'weimaraner',
    'welsh_springer_spaniel', 'west_highland_white_terrier', 'whippet',
    'wire-haired_fox_terrier', 'yorkshire_terrier'
]
    max_index = np.argmax(predictions)
    breed_name = dog_breeds[max_index]
    return breed_name

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
