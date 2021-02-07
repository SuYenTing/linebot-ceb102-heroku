#!/usr/bin/env python
# coding: utf-8

# 載入相關套件
import datetime
import json
import mysql.connector
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, TextSendMessage

# 讀取linebot和mysql連線資訊
secretFile = json.load(open('secretFile.json', 'r'))

# 讀取LineBot驗證資訊
line_bot_api = LineBotApi(secretFile['channelAccessToken'])
handler = WebhookHandler(secretFile['channelSecret'])

# 讀取資料庫關鍵字對應訊息
conn = mysql.connector.connect(host=secretFile['host'], 
                               user=secretFile['user'], 
                               password=secretFile['password'],
                               port=secretFile['port'], 
                               database=secretFile['dbName'])
cursor = conn.cursor()
query = "select * from linebot.keyword;"
cursor.execute(query)
keywordInfoData = cursor.fetchall()
conn.close()

# 關鍵字列表
keys = set()
for key in keywordInfoData:
    keys.add(key[0])
    
# 提醒使用者可輸入關鍵字訊息(將所有關鍵字列出來)
remindKeyMsg = '糟糕! 我聽不懂您在說什麼? \n我目前可以輸入的關鍵字有：\n\n'
for key in keys:
    remindKeyMsg = remindKeyMsg + ' > ' + key + '\n'
remindKeyMsg = remindKeyMsg + '\n您可以嘗試輸入看看唷!\n例如：「小幫手 筆記」'

# 判斷使用者輸入'小幫手'訊息是否有關鍵字詞 若有做對應訊息處理
def FindKeyWordInText(text, userId):
    
    # 比對關鍵字詞 若有則輸出對應訊息
    for key in keywordInfoData:
        if key[1] in text:
            return(key[2])
        
    # 若比對不到關鍵字 則紀錄使用者輸入訊息 並回傳提示關鍵字訊息
    # 使用者輸入找不到的訊息可做為之後開發參考
    conn = mysql.connector.connect(host=secretFile['host'], 
                                       user=secretFile['user'], 
                                       password=secretFile['password'],
                                       port=secretFile['port'], 
                                       database=secretFile['dbName'])
    cursor = conn.cursor()
    query = 'INSERT INTO linebot.msg (user_id, time, msg) VALUES (%s, %s, %s)'
    value = (userId, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), text)
    cursor.execute(query, value)
    conn.commit()
    conn.close()
    
    return(remindKeyMsg)

# 推播群組的ID
lineGroupID = secretFile['lineGroupID']

# 建立Flask
app = Flask(__name__)

# linebot接收訊息
@app.route("/", methods=['GET', 'POST'])
def callback():
    
    # 處理GET
    if request.method == 'GET':
        
        outstr = '''
        <h3>Line機器人-CEB102課程小幫手</h3>
        <span>您好！ 關於此Line機器人的詳細資訊可參考<a href='https://github.com/SuYenTing/linebot-ceb102-heroku'>GitHub專案說明</a></span>
        '''
        return outstr
    
    # 處理POST
    elif request.method == 'POST':
        
        # get X-Line-Signature header value: 驗證訊息來源
        signature = request.headers['X-Line-Signature']

        # get request body as text: 讀取訊息內容
        body = request.get_data(as_text=True)
        app.logger.info("Request body: " + body)

        # handle webhook body
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            print("Invalid signature. Please check your channel access token/channel secret.")
            abort(400)

        return 'OK'

# linebot處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    # linebot關鍵字回傳訊息
    if '小幫手' in event.message.text:
        replyMsg = FindKeyWordInText(text=event.message.text, userId=event.source.user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=replyMsg))

# 開始運作Flask
if __name__ == "__main__":
    app.run(host='0.0.0.0')
