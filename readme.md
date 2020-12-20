##### これはポケモンカードゲームの公式Q&Aページから特定のbotでツイートするプログラムです
- テストコマンド
``` python
heroku login
heroku run python app.py -a ptcg-twitter-bot
```
- 参考
  - tweet developer公式   
    https://developer.twitter.com/en/account/get-started    
  - developerへの登録   
    https://qiita.com/yokoh9/items/760e432ebd39040d5a0f
  - seleniumの使い方    
  　https://tanuhack.com/stable-selenium/   
  - herokuでのスクレイピングのやり方   
    https://tanuhack.com/selenium-bs4-heroku/#buildpack
  - herokuでの定期実行の方法   
    https://kuroyagikun.com/python-twitter-bot-heroku/    
  - tweet方法   
    - twitterライブラリを使う   
      https://qiita.com/yuki_bg/items/96a1608aa3f3225386b6    
    - ライブラリを使わない    
      - タイムラインの取得   
        https://quzee.hatenablog.com/entry/2016/05/08/232539    
      - 複数画像のツイート   
        https://qiita.com/sugurunatsuno/items/8899dacbabfab43f6ee8    
