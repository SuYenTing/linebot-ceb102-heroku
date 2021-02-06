# Line聊天機器人-CEB102課程小幫手(Heroku版本)

## 簡介

這是依據我前一個專案[Line聊天機器人-CEB102課程小幫手](https://github.com/SuYenTing/linebot-ceb102)，將Line機器人由Dokcer部署的方式改為Heroku部署，詳細說明可以參考我的[部落格文章](https://suyenting.github.io/post/linebot-ceb102-class-helper-heroku/)。

## 檔案說明

* clock.py：Python程式碼，主要用於Line機器人定時推播訊息到群組，以及自動喚醒Heroku服務功能，裡面有撰寫APScheduler套件的程式碼。

* main.py：Python Flask程式碼，主要用於Line機器人在接收使用者訊息後，判斷要回應的訊息。

* Procfile：讓Heroku知道部署時對應的服務與要執行的檔案。

* requirements.txt：讓Heroku知道部署時需要安裝的Python套件。

* runtime.txt：讓Heroku知道部署時要安裝的Python版本。

* secretFile.json：此為LineBot的token權限與資料庫帳密，main.py和clock.py兩支程式會使用到此資料。此檔案因為私人資訊，故此檔案只留下格式提供參考。
