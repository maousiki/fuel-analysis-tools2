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

    df["運転時間_分"] = df["走行時間"].apply(convert_time_to_minutes)
    df["アイドリング時間_分"] = 0  # 列がないため、暫定的に0とする
    df["走行距離_km"] = pd.to_numeric(df["走行距離"], errors="coerce")  # 列名を修正

    df["アイドリング率_％"] = (df["アイドリング時間_分"] / df["運転時間_分"] * 100).round(2)
    df["平均速度_km_per_h"] = (df["走行距離_km"] / (df["運転時間_分"] / 60)).round(2)

    fuel_efficiency = 3.5
    df["燃料使用量_L"] = (df["走行距離_km"] / fuel_efficiency).round(2)
    df["燃料費_円"] = (df["燃料使用量_L"] * fuel_price).round(0)

    df["運行日"] = pd.to_datetime(df["日付"], errors="coerce")  # '運行日' がない場合の対応
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
        if st.radio("表示形式（燃料費）", ["表", "グラフ"], key="graph1") == "グラフ":
            st.bar_chart(df.set_index("乗務員")["燃料費_円"])
        else:
            st.dataframe(df[["乗務員", "燃料費_円"]].set_index("乗務員"), height=500), height=500)

        st.subheader("📊 ドライバー別：アイドリング率")
        if st.radio("表示形式（アイドリング率）", ["表", "グラフ"], key="graph2") == "グラフ":
            st.bar_chart(df.set_index("乗務員")["アイドリング率_％"])
        else:
            st.dataframe(df[["乗務員", "アイドリング率_％"]].set_index("乗務員"), height=500), height=500)

        st.subheader("📊 ドライバー別：平均速度")
        if st.radio("表示形式（平均速度）", ["表", "グラフ"], key="graph3") == "グラフ":
            st.bar_chart(df.set_index("乗務員")["平均速度_km_per_h"])
        else:
            st.dataframe(df[["乗務員", "平均速度_km_per_h"]].set_index("乗務員"), height=500), height=500)

        # アドバイス表示（チェックボックスでON/OFF）
        if st.checkbox("📝 アドバイスを表示する"):
            st.subheader("🛠 ドライバー別アドバイス")
            for _, row in df.iterrows():
                advice = []
                if row["アイドリング率_％"] > 100:
                    advice.append("アイドリング時間が長めです。不要なアイドリングを避けましょう。")
                if row["平均速度_km_per_h"] < 20:
                    advice.append("平均速度が低めです。交通状況に応じて速度一定を意識すると燃費改善に効果的です。")
                if row["燃料費_円"] > df["燃料費_円"].quantile(0.75):
                    advice.append("燃料費がやや高めです。走行ルートや待機時間の見直しを検討しましょう。")

                if advice:
                    st.markdown(f"**🚚 {row['乗務員']} さんへのアドバイス：**")
                    for a in advice:
                        st.markdown(f"- {a}")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
