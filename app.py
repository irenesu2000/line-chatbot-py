from flask import Flask, request, abort, url_for
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
import os
import requests
from PIL import Image
import tensorflow as tf
from keras.models import load_model 
import gdown
import numpy as np

app = Flask(__name__)
channel_access_token = os.environ.get('CHANNEL_ACCESS_TOKEN', 'vUK0c7t5wTx/FuYhwUDoNI5AQVjvvlwjPFSR6Rl698i0tf4gzMO9zcvZUx4KPEJHMlDOHMPcLIY2r5OSkByRNZWWHMZzt+78Pxyp38iCL4nX+HwF8jcje70PGtc+Wn4aGUKBBr2WA8EGzdMtJNhIWAdB04t89/1O/w1cDnyilFU=')
line_bot_api = LineBotApi(channel_access_token)
channe_secret = os.environ.get('CHANNEL_SECRET', 'd89ecc5d7744bb60ae98b2f3b487c6f5')
handler = WebhookHandler(channe_secret)


model = None
def get_model():
    global model
    if model is None:
        url = 'https://drive.google.com/uc?id=1dfC8DQdJHvvU5x2PYGIj-t5OkZFXWJag'
        output = 'model_last.h5'
        gdown.download(url, output, quiet=False)
        model = load_model(output)
    return model

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
         # Use the mounted disk path to store the image
        file_path = f"{message_id}.jpg"
        # Log: Received an image message
        app.logger.info(f"Received image message: {message_id}")
        # Store image
        with open(file_path, "wb") as f:
            for chunk in message_content.iter_content():
                f.write(chunk)
        # 检查文件是否已经成功保存
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # Log: Image stored
            app.logger.info(f"Image stored: {file_path}")
            
            img = process_image(file_path)
            # Log: Image processing done
            app.logger.info("Image processing done")
            test_image = np.expand_dims(img, axis=0)
            model = get_model()
            app.logger.info("------------get model------------")
            predictions = model.predict(test_image)
            app.logger.info("------------Prediction------------")
            predicted_result = predict_breed(predictions)
            app.logger.info("------------Prediction done ------------")
            reply_message = TextSendMessage(text="這茲勾勾4 " +str(predicted_result))
            line_bot_api.reply_message(event.reply_token, reply_message)
            os.remove(file_path)
            app.logger.info("Image file removed after processing")
        else:
            # 处理文件未保存的情况
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="抱歉，照片儲存失敗。")
            )
    except LineBotApiError as e:
        app.logger.error(f"Line Bot API error: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="抱歉，照片處理過程中出現錯誤。")
        )
    except Exception as e:
        app.logger.error(f"Error: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="抱歉，照片處理過程中出現未知錯誤。")
        )
def process_image(image_path, img_size=64):
    # Read in an image file
    IMG_SIZE = 64
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
    '猴狀梗 (affenpinscher)', '阿富汗獵犬 (afghan_hound)', '非洲狩獵犬 (african_hunting_dog)', '艾爾戴爾梗 (airedale)',
    '美國斯塔福郡梗 (american_staffordshire_terrier)', '阿彭策勒牧羊犬 (appenzeller)', '澳洲梗 (australian_terrier)',
    '巴辛吉犬 (basenji)', '巴吉度獵犬 (basset)', '米格魯 (beagle)', '貝靈頓梗 (bedlington_terrier)', '伯恩山犬 (bernese_mountain_dog)',
    '黑棕浣熊獵犬 (black-and-tan_coonhound)', '布倫海姆獵犬 (blenheim_spaniel)', '聖休伯特獵犬 (bloodhound)', '藍點獵犬 (bluetick)',
    '邊境牧羊犬 (border_collie)', '邊境梗 (border_terrier)', '俄羅斯獵狼犬 (borzoi)', '波士頓梗 (boston_bull)',
    '法蘭德斯牧牛犬 (bouvier_des_flandres)', '拳師犬 (boxer)', '布魯塞爾格裡芬犬 (brabancon_griffon)', '布里亞德牧羊犬 (briard)',
    '布列塔尼獵犬 (brittany_spaniel)', '鬥牛獒 (bull_mastiff)', '凱恩梗 (cairn)', '卡地根威爾士柯基犬 (cardigan)',
    '切薩皮克海灣拾回犬 (chesapeake_bay_retriever)', '吉娃娃 (chihuahua)', '鬆獅犬 (chow)', '克倫伯獵犬 (clumber)', 
    '可卡犬 (cocker_spaniel)', '科利牧羊犬 (collie)', '捲毛拾回犬 (curly-coated_retriever)', '丹迪丁蒙梗 (dandie_dinmont)', 
    '亞洲野犬 (dhole)', '澳洲野狗 (dingo)', '杜賓犬 (doberman)', '英國獵狐犬 (english_foxhound)', 
    '英格蘭雪達犬 (english_setter)', '英國史賓格獵犬 (english_springer)', '恩特勒布赫山犬 (entlebucher)', '愛斯基摩犬 (eskimo_dog)', 
    '平毛拾回犬 (flat-coated_retriever)', '法國鬥牛犬 (french_bulldog)', '德國牧羊犬 (german_shepherd)', '德國短毛指示犬 (german_short-haired_pointer)', 
    '巨型雪納瑞 (giant_schnauzer)', '金毛尋回犬 (golden_retriever)', '戈登雪達犬 (gordon_setter)', '大丹犬 (great_dane)', 
    '大比利牛斯山犬 (great_pyrenees)', '大瑞士山地犬 (greater_swiss_mountain_dog)', '格羅寧達爾 (groenendael)', '伊比薩獵犬 (ibizan_hound)', 
    '愛爾蘭雪達犬 (irish_setter)', '愛爾蘭梗 (irish_terrier)', '愛爾蘭水獵犬 (irish_water_spaniel)', '愛爾蘭狼犬 (irish_wolfhound)', 
    '意大利灰狗 (italian_greyhound)', '日本獵犬 (japanese_spaniel)', '荷蘭卷毛狗 (keeshond)', '澳洲牧羊犬 (kelpie)', 
    '凱瑞藍梗 (kerry_blue_terrier)', '科莫多犬 (komondor)', '匈牙利牧羊犬 (kuvasz)', '拉布拉多拾回犬 (labrador_retriever)', 
    '湖區梗 (lakeland_terrier)', '李昂伯格犬 (leonberg)', '拉薩犬 (lhasa)', '阿拉斯加雪橇犬 (malamute)', 
    '比利時瑪利諾斯犬 (malinois)', '馬爾濟斯犬 (maltese_dog)', '墨西哥無毛犬 (mexican_hairless)', '迷你品丘犬 (miniature_pinscher)', 
    '迷你貴賓犬 (miniature_poodle)', '迷你雪納瑞 (miniature_schnauzer)', '紐芬蘭犬 (newfoundland)', '諾福克梗 (norfolk_terrier)', 
    '挪威獵鹿犬 (norwegian_elkhound)', '諾威奇梗 (norwich_terrier)', '老英格蘭牧羊犬 (old_english_sheepdog)', '水獺獵犬 (otterhound)', 
    '蝴蝶犬 (papillon)', '北京犬 (pekinese)', '彭布羅克威爾士柯基犬 (pembroke)', '博美犬 (pomeranian)', '巴哥犬 (pug)', 
    '紅骨獵犬 (redbone)', '羅德西亞背脊犬 (rhodesian_ridgeback)', '羅威那犬 (rottweiler)', '聖伯納犬 (saint_bernard)', 
    '沙魯基犬 (saluki)', '薩摩耶犬 (samoyed)', '舍伯奇犬 (schipperke)', '蘇格蘭梗 (scotch_terrier)', '蘇格蘭獵鹿犬 (scottish_deerhound)', 
    '塞利哈姆梗 (sealyham_terrier)', '謝特蘭牧羊犬 (shetland_sheepdog)', '柴犬 (shiba)', '西施犬 (shih-tzu)', 
    '西伯利亞哈士奇 (siberian_husky)', '絲毛梗 (silky_terrier)', '軟毛小麥梗 (soft-coated_wheaten_terrier)', '斯塔福郡鬥牛梗 (staffordshire_bullterrier)', 
    '標準貴賓犬 (standard_poodle)', '標準雪納瑞 (standard_schnauzer)', '薩塞克斯獵犬 (sussex_spaniel)', '藏獒 (tibetan_mastiff)', 
    '藏獒 (tibetan_terrier)', '玩具貴賓犬 (toy_poodle)', '玩具梗 (toy_terrier)', '匈牙利短毛獵犬 (vizsla)', '沃克獵犬 (walker_hound)', 
    '威瑪獵犬 (weimaraner)', '威爾斯濱獵犬 (welsh_springer_spaniel)', '西高地白梗 (west_highland_white_terrier)', '惠比特犬 (whippet)', 
    '硬毛狐狸梗 (wire-haired_fox_terrier)', '約克夏梗 (yorkshire_terrier)'
]

    max_index = np.argmax(predictions)
    breed_name = dog_breeds[max_index]
    return breed_name
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
