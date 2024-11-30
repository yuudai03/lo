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
                    forecast = "\n".join([f"{t.split('T')[0]}: {w.split(' / ')[0]}" for t, w in zip(weather_data[0]["timeSeries"][0]["timeDefines"], area["weathers"])])
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