import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib


st.title("スマブラSP戦績記録アプリ")

char_ls = [
    "マリオ", "ドンキーコング", "リンク", "サムス", "ダークサムス", "ヨッシー", "カービィ", "フォックス", "ピカチュウ", "ルイージ", "ネス", "キャプテン・ファルコン", "プリン", "ピーチ", "デイジー", "クッパ", "アイスクライマー", "シーク", "ゼルダ", "ドクターマリオ", "ピチュー", "ファルコ", "マルス", "ルキナ", "こどもリンク", "ガノンドロフ", "ミュウツー", "ロイ", "クロム", "Mr.ゲーム＆ウォッチ", "メタナイト", "ピット", "ブラックピット", "ゼロスーツサムス", "ワリオ", "スネーク", "アイク", "ポケモントレーナー", "ゼニガメ", "フシギソウ", "リザードン", "ディディーコング", "リュカ", "ソニック", "デデデ", "ピクミン＆オリマー", "ルカリオ", "ロボット", "トゥーンリンク", "ウルフ", "むらびと", "ロックマン", "Wii Fit トレーナー", "ロゼッタ＆チコ", "リトル・マック", "ゲッコウガ", "Miiファイター", "Mii 格闘タイプ", "Mii 剣術タイプ", "Mii 射撃タイプ", "パルテナ", "パックマン", "ルフレ", "シュルク", "クッパJr.", "ダックハント", "リュウ", "ケン", "クラウド", "カムイ", "ベヨネッタ", "インクリング", "リドリー", "シモン", "リヒター", "キングクルール", "しずえ", "ガオガエン", "パックンフラワー", "ジョーカー", "勇者", "バンジョー＆カズーイ", "テリー", "ベレト / ベレス", "ミェンミェン", "スティーブ / アレックス", "セフィロス", "ホムラ / ヒカリ", "ホムラ", "ヒカリ", "カズヤ", "ソラ"
]

tab1, tab2, tab3 = st.tabs(["📍戦績を登録する", "👀戦績表示(個人)", '統計情報'])


# 戦績入力フォーム
with tab1:
    conn = sqlite3.connect("smash.db")
    cursor = conn.cursor()

    with st.form("match_form"):
        user = st.text_input("ユーザー名")
        own_character = st.selectbox("自キャラの名前", char_ls)
        opponent_character = st.selectbox("相手キャラの名前", char_ls)
        rating = st.number_input("戦闘力", min_value=0)
        result = st.selectbox("試合結果", ["勝ち", "負け"])
        minor_rule = st.selectbox(
            "優先ルール", ["不明", "相手"], placeholder="自分のルールでなければ相手を選んでください。(2ストック、アイテム有など)")
        lag = st.selectbox("ラグの有無", ["無", "有"],
                           placeholder="ラグがあった場合は有を選んでください。")
        bad_manner = st.selectbox(
            "煽りや切断", ["無", "有"], placeholder="煽りや切断などがあった場合は有を選んでください。")
        one_pattern = st.selectbox(
            "ワンパターン戦法", ["無", "有"], placeholder="相手がワンパターン戦法だった場合は有を選んでください。")
        smart_player = st.selectbox("相手のプレイスタイル", [
                                    "普通・荒い", "丁寧"], placeholder="相手のプレイスタイルが丁寧(見てから行動する)だと感じた場合は丁寧を選んでくださ  い。")
        date = st.date_input("日付")
        time_zone = st.selectbox("時間帯", ["0:00~0:59", "1:00~1:59", "2:00~2:59", "3:00~3:59", "4:00~4:59", "5:00~5:59", "6:00~6:59",  "7:00~7:59", "8:00~8:59", "9:00~9:59", "10:00~10:59", "11:00~11:59",
                                 "12:00~12:59", "13:00~13:59", "14:00~14:59", "15:00~15:59", "16:00~16:59", "17:00~17:59", "18:00~18:59",   "19:00~19:59", "20:00~20:59", "21:00~21:59", "22:00~22:59", "23:00~23:59"])
        submitted = st.form_submit_button("戦績を追加")
        if submitted:
            cursor.execute("INSERT INTO matches (user, own_character, opponent_character, rating, result, minor_rule,lag,bad_manner,    one_pattern,smart_player,date,time_zone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                user, own_character, opponent_character, rating, result, minor_rule, lag, bad_manner, one_pattern, smart_player, date,  time_zone))
            conn.commit()
            st.success("戦績を追加しました！")

    # 戦績の表示
    st.subheader("戦績一覧(簡易確認)")
    df = pd.read_sql("SELECT * FROM matches", conn)
    conn.close()
    st.dataframe(df)

# 勝率計算関数


def calculate_win_rate(df, condition=None):
    if condition is not None:  # condition が None でない場合のみフィルタ
        df = df.loc[condition]  # Series を boolean mask として利用
        df = df[condition]
    wins = df[df["result"] == "勝ち"].shape[0]
    total = df.shape[0]
    return wins / total if total > 0 else 0


with tab2:
    conn = sqlite3.connect("smash.db")
    df = pd.read_sql("SELECT * FROM matches", conn)
    df["date"] = pd.to_datetime(df["date"], format='mixed')
    conn.close()

    st.header("ユーザーごとの戦績")
    user_selected = st.selectbox("ユーザーを選択", df["user"].unique())
    user_df = df[df["user"] == user_selected]

    st.subheader(f"{user_selected}の勝率")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # 全体の勝率
    win_rate = calculate_win_rate(user_df)
    axes[0].pie([win_rate, 1 - win_rate], labels=["勝ち", "負け"],
                autopct='%1.1f%%', colors=['lightblue', 'lightcoral'])
    axes[0].set_title("全体の勝率")

    # 「相手」ルール時の勝率
    rule_win_rate = calculate_win_rate(user_df, user_df["minor_rule"] == "相手")
    axes[1].pie([rule_win_rate, 1 - rule_win_rate], labels=["勝ち", "負け"],
                autopct='%1.1f%%', colors=['lightgreen', 'lightcoral'])
    axes[1].set_title("優先ルール: 相手")

    # ワンパターン戦法「有」の勝率
    one_pattern_win_rate = calculate_win_rate(
        user_df, user_df["one_pattern"] == "有")
    axes[2].pie([one_pattern_win_rate, 1 - one_pattern_win_rate],
                labels=["勝ち", "負け"], autopct='%1.1f%%', colors=['orange', 'lightcoral'])
    axes[2].set_title("ワンパターン戦法: 有")

    st.pyplot(fig)

    # キャラクターごとの勝率
    st.subheader("キャラクターごとの勝率")
    char_win_rates = user_df[user_df["result"] == "勝ち"].groupby(
        "own_character").size() / user_df.groupby("own_character").size()

    fig, ax = plt.subplots()
    char_win_rates.sort_values().plot(kind="barh", ax=ax, color="skyblue")
    ax.set_title("キャラクターごとの勝率")
    st.pyplot(fig)

    # # キャラクターを選択
    # st.subheader("キャラクターごとの戦闘力推移")
    # selected_characters = st.multiselect(
    #     "キャラクターを選択", user_df["own_character"].unique())
    # if selected_characters:
    #     fig, ax = plt.subplots()
    #     for character in selected_characters:
    #         char_data = user_df[user_df["own_character"]
    #                             == character].sort_values("date")
    #         ax.plot(char_data["date"], char_data["rating"], label=character)

    #     ax.set_title("キャラクターごとの戦闘力推移")
    #     ax.set_xlabel("日付")
    #     ax.set_ylabel("戦闘力")
    #     ax.legend()
    #     st.pyplot(fig)

    # 時間帯ごとの勝率
    st.subheader("時間帯ごとの勝率")
    time_win_rates = user_df[user_df["result"] == "勝ち"].groupby(
        "time_zone").size() / user_df.groupby("time_zone").size()

    fig, ax = plt.subplots()
    time_win_rates.sort_index().plot(kind="bar", ax=ax, color="lightgreen")
    ax.set_title("時間帯ごとの勝率")
    st.pyplot(fig)

    # 相手キャラごとの勝率（ヒートマップ）
    st.subheader("相手キャラごとの勝率")
    opponent_win_rates = user_df[user_df["result"] == "勝ち"].groupby(
        "opponent_character").size() / user_df.groupby("opponent_character").size()

    fig, ax = plt.subplots(figsize=(10, 15))
    sns.heatmap(opponent_win_rates.to_frame(), annot=True,
                fmt=".2f", cmap="coolwarm", linewidths=1, ax=ax)
    ax.set_title("相手キャラごとの勝率")
    st.pyplot(fig)

    # ラグの割合
    st.subheader("ラグの割合")
    lag_counts = user_df["lag"].value_counts()

    fig, ax = plt.subplots()
    ax.pie(lag_counts, labels=lag_counts.index,
           autopct='%1.1f%%', colors=['lightcoral', 'lightblue'])
    ax.set_title("ラグの割合")
    st.pyplot(fig)

with tab3:
    conn = sqlite3.connect("smash.db")
    df = pd.read_sql("SELECT * FROM matches", conn)
    df["date"] = pd.to_datetime(df["date"], format='mixed')
    conn.close()

    st.header("全体の統計情報")

    # キャラクターごとの勝率
    st.subheader("キャラクターごとの勝率")
    char_win_rates = df[df["result"] == "勝ち"].groupby(
        "own_character").size() / df.groupby("own_character").size()

    fig, ax = plt.subplots()
    char_win_rates.sort_values().plot(kind="barh", ax=ax, color="skyblue")
    ax.set_title("キャラクターごとの勝率")
    st.pyplot(fig)

    # 時間帯ごとの勝率
    st.subheader("時間帯ごとの勝率")
    time_win_rates = df[df["result"] == "勝ち"].groupby(
        "time_zone").size() / df.groupby("time_zone").size()

    fig, ax = plt.subplots()
    time_win_rates.sort_index().plot(kind="bar", ax=ax, color="lightgreen")
    ax.set_title("時間帯ごとの勝率")
    st.pyplot(fig)

    # ラグの割合
    st.subheader("ラグの割合")
    lag_counts = df["lag"].value_counts()

    fig, ax = plt.subplots()
    ax.pie(lag_counts, labels=lag_counts.index,
           autopct='%1.1f%%', colors=['lightcoral', 'lightblue'])
    ax.set_title("ラグの割合")
    st.pyplot(fig)

    # ラグが発生したキャラクター分布
    st.subheader("ラグが発生したキャラクター分布")
    lagged_characters = df[df["lag"] ==
                           "有"]["opponent_character"].value_counts()

    fig, ax = plt.subplots()
    lagged_characters.sort_values().plot(kind="barh", ax=ax, color="red")
    ax.set_title("ラグが発生したキャラクター分布")
    st.pyplot(fig)

    # 優先ルール(特殊なルール)の割合
    st.subheader("優先ルールの割合(特殊なルール)")
    rule_counts = df["minor_rule"].value_counts()

    fig, ax = plt.subplots()
    ax.pie(rule_counts, labels=rule_counts.index, autopct='%1.1f%%',
           colors=['lightblue', 'lightgreen', 'orange'])
    ax.set_title("優先ルールの割合(特殊なルール)")
    st.pyplot(fig)
