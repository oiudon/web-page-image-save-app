import PySimpleGUI as sg
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import urllib
import time
import re

# テーマの設定
sg.theme("DarkGray15")

# レイアウトの作成
layout = [[sg.T("◆画像の保存先フォルダを選択してください。")],
          [sg.B(" 保存先 ", k="btn1"), sg.T(k="txt1")],
          [sg.T("◆WebページのURLを入力してください。")],
          [sg.T("url："), sg.I(k="in")],
          [sg.B(" 実行 ", k="btn2"), sg.T("", k="txt2")]]
win = sg.Window("Webページ内画像収集アプリ", layout, font=(None,14), size=(550,180))

# 保存先フォルダ選択部分の作成
savepath = None
def loadFolder():
    global loadname, savepath
    # 保存先フォルダの読み込み
    loadname = sg.popup_get_folder("保存先フォルダを選択してください。")
    
    # 保存先フォルダが選択されなかったらreturnする
    if not loadname:
        return

    # 保存先フォルダの確定
    savepath = Path(loadname)
    win["txt1"].update(savepath)
    win["txt2"].update("")

# 実行部分の作成
def execute():
    # 保存先フォルダが選択されているか確認
    if not savepath:
        sg.PopupTimed("保存先フォルダを選択してください。")
        return
    
    # URLの入力確認
    if v["in"] == "":
        sg.PopupTimed("URLを入力してください。")
        return

    # Webページを取得して解析する
    try:
        load_url = v["in"]
        html = requests.get(load_url)
        soup = BeautifulSoup(html.content, "html.parser")
    except:
        sg.PopupTimed("URLが有効ではありません。")
        return

    # すべてのimgタグを検索しリンクを取得する
    for element in soup.find_all("img"):
        src = element.get("src")

        # 絶対URLを作って画像データを取得する
        image_url = urllib.parse.urljoin(load_url, src)
        imgdata = requests.get(image_url)

        # URLから最後のファイル名を取り出して、保存フォルダとつなげる
        filename = re.sub(r'[\\|/|:|?|"|<|>|\|]', '-', image_url.split("/")[-1])
        out_path = savepath.joinpath(filename)

        # 画像データをファイルに書き出す
        try:
            with open(out_path, mode="wb") as f:
                f.write(imgdata.content)
        except FileNotFoundError:
            sg.PopupTimed("保存先フォルダが見つかりません。")
            return

        # 1回アクセスごとに0.2秒待つ
        time.sleep(0.2)

    win["txt2"].update("保存完了")

while True:
    e, v = win.read()
    if e == "btn1":
        loadFolder()
    if e == "btn2":
        execute()
    if e == None:
        break
win.close()
