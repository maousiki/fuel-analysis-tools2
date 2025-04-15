import streamlit as st
import pandas as pd
import os

# 時間を分に変換する関数
def convert_time_to_minutes(time_str):
    try:
        hours, minutes = map(int, str(time_str).split(":"))
        return hours * 60 + minutes
    except:
        return 0

# CSVデータを処理する関数
def process_csv_data(uploaded_file, fuel_price):
    df = pd.read_csv(uploaded_file, encoding="cp932")

    df["運転時間_分"] = df["ハンドル時間－時分－"].apply(convert_time_to_minutes)
    df["アイドリング時間_分"] = df["アイドリング－時分－"].apply(convert_time_to_minutes)
    df["走行距離_km"] = pd.to_numeric(df["走行距離－ｋｍ－"], errors="coerce")

    df["アイドリング率_％"] = (df["アイドリング時間_分"] / df["運転時間_分"] * 100).round(2)
    df["平均速度_km_per_h"] = (df["走行距離_km"] / (df["運転時間_分"] / 60)).round(2)

    fuel_efficiency = 3.5
    df["燃料使用量_L"] = (df["走行距離_km"] / fuel_efficiency).round(2)
    df["燃料費_円"] = (df["燃料使用量_L"] * fuel_price).round(0)

    return df[[
        "乗務員", "運行日", "走行距離_km", "運転時間_分", "アイドリング時間_分",
        "アイドリング率_％", "平均速度_km_per_h", "燃料使用量_L", "燃料費_円"
    ]]

# メイン処理
st.title("🚚 燃費見える化くん（Web版）")
st.write("CSVファイルをアップロードすると、燃費やコスト、ランキングが表示されます。")

fuel_price = st.number_input("燃料単価（円/L）を入力してください", value=160, step=1)

uploaded_file = st.file_uploader("CSVファイルを選んでください", type=["csv"])

if uploaded_file is not None:
    try:
        df = process_csv_data(uploaded_file, fuel_price)
        st.success("データを読み込みました！")
        st.dataframe(df)

        # ランキングテーブル表示
        st.subheader("💡 ランキング：燃料費（高い順）")
        st.dataframe(df.sort_values("燃料費_円", ascending=False)[["乗務員", "燃料費_円"]])

        st.subheader("💡 ランキング：アイドリング率（高い順）")
        st.dataframe(df.sort_values("アイドリング率_％", ascending=False)[["乗務員", "アイドリング率_％"]])

        st.subheader("💡 ランキング：平均速度（高い順）")
        st.dataframe(df.sort_values("平均速度_km_per_h", ascending=False)[["乗務員", "平均速度_km_per_h"]])

        # グラフ表示
        st.subheader("📊 ドライバー別：燃料費")
        st.bar_chart(df.set_index("乗務員")["燃料費_円"])

        st.subheader("📊 ドライバー別：アイドリング率")
        st.bar_chart(df.set_index("乗務員")["アイドリング率_％"])

        st.subheader("📊 ドライバー別：平均速度")
        st.bar_chart(df.set_index("乗務員")["平均速度_km_per_h"])

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
