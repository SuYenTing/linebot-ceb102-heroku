# Line機器人排程程式
# 2021/02/05 蘇彥庭
import datetime
import urllib
import json
import mysql.connector
from apscheduler.schedulers.blocking import BlockingScheduler
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage

# 讀取linebot和mysql連線資訊
secretFile = json.load(open('secretFile.json', 'r'))

# 讀取LineBot驗證資訊
line_bot_api = LineBotApi(secretFile['channelAccessToken'])
handler = WebhookHandler(secretFile['channelSecret'])

# 推播群組的ID
lineGroupID = secretFile['lineGroupID']


# 課前提醒任務
def RemindClass(status):
    # 讀取今日行程資訊
    conn = mysql.connector.connect(host=secretFile['host'],
                                   user=secretFile['user'],
                                   password=secretFile['password'],
                                   port=secretFile['port'],
                                   database=secretFile['dbName'])
    cursor = conn.cursor()
    query = "select * from linebot.curriculum where dates = '" + str(
        datetime.datetime.now().strftime('%Y-%m-%d')) + "';"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()

    # 判斷今日是否有行程 若沒有則不做任何動作
    if result:

        # 若有行程 則進行判斷是否要推播
        for row in result:

            # 行程資訊
            period = row[1]
            className = row[2]
            principal = row[3]

            # 判斷行程期間是否與當前期間一致 若一致則進行對應操作
            if status == period:

                if period == '上午':

                    if principal:
                        msg = '早安! 今早的課程是「' + className + '」\n大家請記得要打卡唷!\n教室日誌要麻煩 ' + principal[-2::] + ' 填寫唷!'
                    else:
                        msg = '早安! 今早的課程是「' + className + '」\n大家請記得要打卡唷!'
                    line_bot_api.push_message(lineGroupID, TextSendMessage(text=msg))

                elif period == '下午':

                    if principal:
                        msg = '午安! 下午的課程是「' + className + '」\n大家請記得要打卡唷!\n教室日誌要麻煩 ' + principal[-2::] + ' 填寫唷!'
                    else:
                        msg = '午安! 下午的課程是「' + className + '」\n大家請記得要打卡唷!'
                    line_bot_api.push_message(lineGroupID, TextSendMessage(text=msg))

                elif period == '夜間':

                    if principal:
                        msg = '晚上好! 晚上的課程是「' + className + '」\n大家請記得要打卡唷!\n教室日誌要麻煩 ' + principal[-2::] + ' 填寫唷!'
                    else:
                        msg = '晚上好! 晚上的課程是「' + className + '」\n大家請記得要打卡唷!'
                    line_bot_api.push_message(lineGroupID, TextSendMessage(text=msg))


# 提醒明日課程任務
def RemindTmrClass():
    # 讀取明日行程資訊
    conn = mysql.connector.connect(host=secretFile['host'],
                                   user=secretFile['user'],
                                   password=secretFile['password'],
                                   port=secretFile['port'],
                                   database=secretFile['dbName'])
    cursor = conn.cursor()
    query = "select * from linebot.curriculum where dates = '" + str(
        (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')) + "';"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()

    # 判斷明日是否有行程 若沒有則不做任何動作
    if result:
        msg = '提醒大家 明日有上課唷!\n課程資訊如下: \n'
        for row in result:
            period = row[1]
            className = row[2]
            msg = msg + period + ' ' + className + '\n'
        msg = msg + '記得要來唷!'
        line_bot_api.push_message(lineGroupID, TextSendMessage(text=msg))


# 防止睡眠
def DoNotSleep():
    url = "https://linebotceb102.herokuapp.com/"
    conn = urllib.request.urlopen(url)


# 開始建立排程任務
sched = BlockingScheduler()

# 早上課程推播任務
sched.add_job(RemindClass, trigger='cron', args=('上午',), id='morning_job', hour=8, minute=45)

# 中午課程推播任務
sched.add_job(RemindClass, trigger='cron', args=('下午',), id='afternoon_job', hour=13, minute=15)

# 夜間課程推播任務
sched.add_job(RemindClass, trigger='cron', args=('夜間',), id='night_job', hour=18, minute=15)

# 晚上提醒課程推播任務
sched.add_job(RemindTmrClass, trigger='cron', id='tmrClass_job', hour=21, minute=0)

# 防止自動休眠
sched.add_job(DoNotSleep, trigger='interval', id='doNotSleeps_job', minutes=20)

# 啟動排程
sched.start()
