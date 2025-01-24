import json
import os
from datetime import datetime

# daily.jsonのパスを定義
daily_json_path = os.path.join(os.path.dirname(__file__), '../daily.json')

# daily.jsonを読み込む関数
def read_daily_json():
    with open(daily_json_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# 今日の日付を取得する関数
def get_today_date():
    return datetime.now().strftime('%Y-%m-%d')

# daily.jsonに今日の日付を書き出す関数
def write_daily_json(date):
    data = {'date': date}
    with open(daily_json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

# メイン処理
def main():
    # daily.jsonを読み込む
    daily_data = read_daily_json()
    print('Current daily.json:', daily_data)

    # 今日の日付を取得
    today_date = get_today_date()
    print('Today\'s date:', today_date)

    # daily.jsonに今日の日付を書き出す
    write_daily_json(today_date)
    print('Updated daily.json with today\'s date.')

# メイン処理を実行
if __name__ == '__main__':
    main()
