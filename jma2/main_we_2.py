import sqlite3
import json

# データベースファイル
db_file = "jma2/weather.db"

# JSONファイルの読み込み
json_file = "jma2/area.json"
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# データベースの作成・接続
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# テーブルの作成
cursor.execute("""
CREATE TABLE IF NOT EXISTS regions (
    region_code TEXT PRIMARY KEY,
    region_name TEXT
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS prefectures (
    prefecture_code TEXT PRIMARY KEY,
    prefecture_name TEXT,
    region_code TEXT,
    FOREIGN KEY (region_code) REFERENCES regions (region_code)
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS subregions (
    subregion_code TEXT PRIMARY KEY,
    subregion_name TEXT,
    prefecture_code TEXT,
    FOREIGN KEY (prefecture_code) REFERENCES prefectures (prefecture_code)
);
""")

# weatherテーブルの作成
cursor.execute("""
CREATE TABLE IF NOT EXISTS weather (
    weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subregion_code TEXT,
    weather_description TEXT,
    date TEXT,
    FOREIGN KEY (subregion_code) REFERENCES subregions (subregion_code)
);
""")

# データの挿入
centers = data.get("centers", {})
offices = data.get("offices", {})
class10s = data.get("class10s", {})

# 地方データの挿入
for region_code, region_info in centers.items():
    region_name = region_info.get("name")
    cursor.execute("INSERT OR IGNORE INTO regions (region_code, region_name) VALUES (?, ?);", (region_code, region_name))

# 都道府県データの挿入
for prefecture_code, prefecture_info in offices.items():
    prefecture_name = prefecture_info.get("name")
    region_code = prefecture_info.get("parent")
    cursor.execute("""
        INSERT OR IGNORE INTO prefectures (prefecture_code, prefecture_name, region_code)
        VALUES (?, ?, ?);
    """, (prefecture_code, prefecture_name, region_code))

# 細分化地域データの挿入
for subregion_code, subregion_info in class10s.items():
    subregion_name = subregion_info.get("name")
    prefecture_code = subregion_info.get("parent")
    cursor.execute("""
        INSERT OR IGNORE INTO subregions (subregion_code, subregion_name, prefecture_code)
        VALUES (?, ?, ?);
    """, (subregion_code, subregion_name, prefecture_code))

# データベース保存と接続の終了
conn.commit()
conn.close()
print("データベース作成完了")


import sqlite3
import requests
import time
from datetime import datetime

# データベースファイル
db_file = "jma2/weather.db"

def get_weather_data(prefecture_code, subregion_code):
    try:
        url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{prefecture_code}.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        weather_data = response.json()

        results = []
        for time_series in weather_data:
            for time_series_entry in time_series.get('timeSeries', []):
                time_defines = time_series_entry.get('timeDefines', [])
                for i, time_define in enumerate(time_defines):
                    date = datetime.strptime(time_define, '%Y-%m-%dT%H:%M:%S%z').date()
                    for area in time_series_entry.get('areas', []):
                        if area["area"]["code"] == subregion_code:
                            weathers = area.get("weathers", [])
                            if weathers:
                                weather_description = weathers[i]
                                results.append((subregion_code, weather_description, str(date)))
        return results
    except requests.exceptions.RequestException as e:
        print(f"天気データ取得エラー ({subregion_code}): {e}")
        return []
    except KeyError as e:
        print(f"JSON解析エラー: キーが見つかりません ({e})")
        return []

def save_weather_data():
    conn = sqlite3.connect(db_file, timeout=30)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subregions.prefecture_code, subregions.subregion_code 
        FROM subregions 
        JOIN prefectures ON subregions.prefecture_code = prefectures.prefecture_code
    """)
    regions = cursor.fetchall()

    for prefecture_code, subregion_code in regions:
        print(f"地域: {subregion_code}の天気を取得中...")
        weather_data = get_weather_data(prefecture_code, subregion_code)
        for (subregion_code, weather_description, date) in weather_data:
            cursor.execute("INSERT OR REPLACE INTO weather (subregion_code, weather_description, date) VALUES (?, ?, ?)", (subregion_code, weather_description, date))
            print(f"天気情報を保存: {subregion_code} - {weather_description} (日付: {date})")

    conn.commit()
    conn.close()

save_weather_data()

import sqlite3
import json

# データベースファイル
db_file = "jma2/weather.db"

# JSONファイルの読み込み
json_file = "jma2/area.json"
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# データベースの作成・接続
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# テーブルの作成
cursor.execute("""
CREATE TABLE IF NOT EXISTS regions (
    region_code TEXT PRIMARY KEY,
    region_name TEXT
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS prefectures (
    prefecture_code TEXT PRIMARY KEY,
    prefecture_name TEXT,
    region_code TEXT,
    FOREIGN KEY (region_code) REFERENCES regions (region_code)
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS subregions (
    subregion_code TEXT PRIMARY KEY,
    subregion_name TEXT,
    prefecture_code TEXT,
    FOREIGN KEY (prefecture_code) REFERENCES prefectures (prefecture_code)
);
""")

# weatherテーブルの作成
cursor.execute("""
CREATE TABLE IF NOT EXISTS weather (
    weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subregion_code TEXT,
    weather_description TEXT,
    date TEXT,
    FOREIGN KEY (subregion_code) REFERENCES subregions (subregion_code)
);
""")

# データの挿入
centers = data.get("centers", {})
offices = data.get("offices", {})
class10s = data.get("class10s", {})

# 地方データの挿入
for region_code, region_info in centers.items():
    region_name = region_info.get("name")
    cursor.execute("INSERT OR IGNORE INTO regions (region_code, region_name) VALUES (?, ?);", (region_code, region_name))

# 都道府県データの挿入
for prefecture_code, prefecture_info in offices.items():
    prefecture_name = prefecture_info.get("name")
    region_code = prefecture_info.get("parent")
    cursor.execute("""
        INSERT OR IGNORE INTO prefectures (prefecture_code, prefecture_name, region_code)
        VALUES (?, ?, ?);
    """, (prefecture_code, prefecture_name, region_code))

# 細分化地域データの挿入
for subregion_code, subregion_info in class10s.items():
    subregion_name = subregion_info.get("name")
    prefecture_code = subregion_info.get("parent")
    cursor.execute("""
        INSERT OR IGNORE INTO subregions (subregion_code, subregion_name, prefecture_code)
        VALUES (?, ?, ?);
    """, (subregion_code, subregion_name, prefecture_code))

# データベース保存と接続の終了
conn.commit()
conn.close()
print("データベース作成完了")

import sqlite3
import requests
import time
from datetime import datetime

# データベースファイル
db_file = "jma2/weather.db"

def get_weather_data(prefecture_code, subregion_code):
    try:
        url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{prefecture_code}.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        weather_data = response.json()

        results = []
        for time_series in weather_data:
            for time_series_entry in time_series.get('timeSeries', []):
                time_defines = time_series_entry.get('timeDefines', [])
                for i, time_define in enumerate(time_defines):
                    date = datetime.strptime(time_define, '%Y-%m-%dT%H:%M:%S%z').date()
                    for area in time_series_entry.get('areas', []):
                        if area["area"]["code"] == subregion_code:
                            weathers = area.get("weathers", [])
                            if weathers:
                                weather_description = weathers[i]
                                results.append((subregion_code, weather_description, str(date)))
        return results
    except requests.exceptions.RequestException as e:
        print(f"天気データ取得エラー ({subregion_code}): {e}")
        return []
    except KeyError as e:
        print(f"JSON解析エラー: キーが見つかりません ({e})")
        return []

def save_weather_data():
    conn = sqlite3.connect(db_file, timeout=30)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subregions.prefecture_code, subregions.subregion_code 
        FROM subregions 
        JOIN prefectures ON subregions.prefecture_code = prefectures.prefecture_code
    """)
    regions = cursor.fetchall()

    for prefecture_code, subregion_code in regions:
        print(f"地域: {subregion_code}の天気を取得中...")
        weather_data = get_weather_data(prefecture_code, subregion_code)
        for (subregion_code, weather_description, date) in weather_data:
            cursor.execute("INSERT OR REPLACE INTO weather (subregion_code, weather_description, date) VALUES (?, ?, ?)", (subregion_code, weather_description, date))
            print(f"天気情報を保存: {subregion_code} - {weather_description} (日付: {date})")

    conn.commit()
    conn.close()

save_weather_data()

import flet as ft
import requests

def main(page: ft.Page):
    # ページ設定
    page.title = "気象庁 天気予報アプリ"
    page.window_width = 1000
    page.window_height = 800
    page.theme_mode = "light"
    page.bgcolor = ft.colors.GREY_50

    # 地域データを取得
    def get_area_data():
        try:
            url = "http://www.jma.go.jp/bosai/common/const/area.json"
            response = requests.get(url)
            data = response.json()
            return data
        except Exception as e:
            print(f"地域データ取得エラー: {str(e)}")
            return None

    # 天気予報データを取得
    def get_weather_data(prefecture_code):
        try:
            url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{prefecture_code}.json"
            response = requests.get(url)
            return response.json()
        except Exception as e:
            print(f"天気予報データ取得エラー: {str(e)}")
            return None

    # 市区町村ごとの天気予報表示
    def display_city_forecast(prefecture_code, city_code, city_name):
        weather_data = get_weather_data(prefecture_code)
        if weather_data:
            for area in weather_data[0]["timeSeries"][0]["areas"]:
                if area["area"]["code"] == city_code:
                    forecast = "\n".join([f"{t.split('T')[0]}: {w}" for t, w in zip(weather_data[0]["timeSeries"][0]["timeDefines"], area["weathers"])])
                    main_content.content = ft.Text(
                        f"{city_name}の天気予報:\n{forecast}",
                        size=18
                    )
                    print(f"{city_name}の天気予報:\n{forecast}")
                    page.update()
                    return
        main_content.content = ft.Text("天気予報データを取得できませんでした", size=18)
        page.update()

    # 地域ツリーを作成
    def create_area_tree():
        data = get_area_data()
        if not data:
            return ft.Text("地域データを取得できませんでした")

        area_view = ft.Column(spacing=2)

        for center_code, center_info in data.get("centers", {}).items():
            prefecture_tiles = []
            for office_code, office_info in data.get("offices", {}).items():
                if office_info.get("parent") == center_code:
                    city_tiles = []
                    for local_code, local_info in data.get("class10s", {}).items():
                        if local_info.get("parent") == office_code:
                            city_tiles.append(
                                ft.ListTile(
                                    leading=ft.Icon(ft.icons.LOCATION_CITY),
                                    title=ft.Text(local_info.get("name", "")),
                                    dense=True,
                                    on_click=lambda e, pc=office_code, lc=local_code, ln=local_info.get("name", ""): display_city_forecast(pc, lc, ln)
                                )
                            )

                    prefecture_tiles.append(
                        ft.ExpansionTile(
                            leading=ft.Icon(ft.icons.BUSINESS),
                            title=ft.Text(office_info.get("name", "")),
                            subtitle=ft.Text(f"観測地数: {len(city_tiles)}"),
                            controls=[ft.Column(controls=city_tiles)],
                            expand=False,
                        )
                    )

            if prefecture_tiles:
                area_view.controls.append(
                    ft.Card(
                        content=ft.ExpansionTile(
                            leading=ft.Icon(ft.icons.MAP, color=ft.colors.BLUE),
                            title=ft.Text(f"{center_info.get('name', '')}", weight="bold"),
                            controls=[ft.Column(controls=prefecture_tiles)],
                            expand=False,
                        ),
                        margin=ft.margin.only(bottom=10),
                    )
                )

        return area_view

    # ヘッダー
    header = ft.AppBar(
        title=ft.Text("日本の天気予報アプリ", weight="bold"),
        bgcolor=ft.colors.BLUE,
        color=ft.colors.WHITE,
    )

    # メインコンテンツ
    main_content = ft.Container(
        content=ft.Text("地域を選択してください", size=18),
        padding=20,
        expand=True,
    )

    # 地域リスト
    area_list = create_area_tree()

    # サイドバー
    sidebar = ft.Container(
        content=ft.Column([area_list], spacing=5, scroll=ft.ScrollMode.ALWAYS),  # ここでスクロールを有効にする
        width=300,
        bgcolor=ft.colors.BLUE_50,
        padding=10,
    )

    # レイアウト
    page.add(
        header,
        ft.Row([sidebar, main_content], expand=True),
    )

ft.app(target=main)