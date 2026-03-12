import streamlit as st
import requests
import pandas as pd
import numpy as np
import ta

st.set_page_config(layout="wide")
st.title("Crypto Full Analyzer PRO")

API_KEY = "ضع_مفتاحك"

coin = st.text_input("اكتب رمز العملة مثل BTC أو DOT").upper()

if coin:

    # -----------------------
    # جلب البيانات
    # -----------------------
    url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={coin}&tsym=USD&limit=120&api_key={API_KEY}"
    data = requests.get(url).json()

    data_list = data.get("Data", {}).get("Data", [])

    if not data_list:
        st.error("لا توجد بيانات")
        st.stop()

    df = pd.DataFrame(data_list)

    df["time"] = pd.to_datetime(df["time"], unit="s")
    df["volume"] = df["volumeto"]

    # -----------------------
    # المؤشرات الفنية
    # -----------------------
    df["EMA20"] = ta.trend.ema_indicator(df["close"], window=20)
    df["EMA50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["EMA200"] = ta.trend.ema_indicator(df["close"], window=200)

    rsi_indicator = ta.momentum.RSIIndicator(df["close"])
    df["RSI"] = rsi_indicator.rsi()

    macd_indicator = ta.trend.MACD(df["close"])
    df["MACD"] = macd_indicator.macd()
    df["MACD_signal"] = macd_indicator.macd_signal()

    price = df["close"].iloc[-1]

    # -----------------------
    # الدعم والمقاومة
    # -----------------------
    support = df["low"].tail(20).min()
    resistance = df["high"].tail(20).max()

    # -----------------------
    # فيبوناتشي
    # -----------------------
    high = df["high"].max()
    low = df["low"].min()

    fib_levels = {
        "0.236": high - (high-low)*0.236,
        "0.382": high - (high-low)*0.382,
        "0.5": high - (high-low)*0.5,
        "0.618": high - (high-low)*0.618
    }

    # -----------------------
    # EMA CROSS
    # -----------------------
    ema_signal = "محايد"
    if df["EMA20"].iloc[-2] < df["EMA50"].iloc[-2] and df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]:
        ema_signal = "تقاطع صعودي 🚀"
    if df["EMA20"].iloc[-2] > df["EMA50"].iloc[-2] and df["EMA20"].iloc[-1] < df["EMA50"].iloc[-1]:
        ema_signal = "تقاطع هبوطي"

    # -----------------------
    # MACD CROSS
    # -----------------------
    macd_cross = "محايد"
    if df["MACD"].iloc[-2] < df["MACD_signal"].iloc[-2] and df["MACD"].iloc[-1] > df["MACD_signal"].iloc[-1]:
        macd_cross = "تقاطع صعودي 📈"
    if df["MACD"].iloc[-2] > df["MACD_signal"].iloc[-2] and df["MACD"].iloc[-1] < df["MACD_signal"].iloc[-1]:
        macd_cross = "تقاطع هبوطي"

    # -----------------------
    # كشف تجميع الحيتان
    # -----------------------
    avg_volume = df["volume"].tail(30).mean()
    current_volume = df["volume"].iloc[-1]
    price_change = abs(df["close"].iloc[-1] - df["close"].iloc[-5]) / df["close"].iloc[-5]
    whale_signal = False
    if current_volume > avg_volume * 2 and price_change < 0.04:
        whale_signal = True

    # -----------------------
    # Volume Profile الحقيقي
    # -----------------------
    bins = np.linspace(df["low"].min(), df["high"].max(), 24)
    df["price_bin"] = pd.cut(df["close"], bins)
    vp = df.groupby("price_bin")["volume"].sum().reset_index()
    vp["range"] = vp["price_bin"].apply(lambda x: f"{x.left:.2f}-{x.right:.2f}")
    vp = vp[["range","volume"]]
    vp.columns = ["Price Range","Volume"]

    # -----------------------
    # حساب SCORE
    # -----------------------
    rsi = df["RSI"].iloc[-1]
    score = 0
    if rsi < 35:
        score += 2
    elif rsi < 55:
        score += 1
    if ema_signal == "تقاطع صعودي 🚀":
        score += 3
    if macd_cross == "تقاطع صعودي 📈":
        score += 2
    if whale_signal:
        score += 3
    if price < fib_levels["0.5"]:
        score += 1

    # -----------------------
    # أفضل نقطة شراء
    # -----------------------
    buy_zone = (support + fib_levels["0.618"]) / 2

    # -----------------------
    # الهدف ووقف الخسارة
    # -----------------------
    target = resistance
    stop_loss = support * 0.97

    # -----------------------
    # توقع الحركة القادمة
    # -----------------------
    trend_score = 0
    if rsi < 35:
        trend_score += 2
    elif rsi > 65:
        trend_score -= 2
    if ema_signal == "تقاطع صعودي 🚀":
        trend_score += 2
    elif ema_signal == "تقاطع هبوطي":
        trend_score -= 2
    if macd_cross == "تقاطع صعودي 📈":
        trend_score += 2
    elif macd_cross == "تقاطع هبوطي":
        trend_score -= 2
    if whale_signal:
        trend_score += 2

    if trend_score >= 3:
        prediction = "📈 احتمال صعود"
    elif trend_score <= -3:
        prediction = "📉 احتمال هبوط"
    else:
        prediction = "➡️ حركة عرضية"

    # -----------------------
    # نسبة نجاح الصفقة
    # -----------------------
    success_rate = (score / 11) * 100

    # -----------------------
    # عرض النتائج
    # -----------------------
    st.subheader("السعر الحالي")
    st.write(price)

    st.subheader("الدعم والمقاومة")
    st.write("الدعم:", support)
    st.write("المقاومة:", resistance)

    st.subheader("مستويات فيبوناتشي")
    for k,v in fib_levels.items():
        st.write(k,v)

    st.subheader("EMA Cross")
    st.write(ema_signal)

    st.subheader("MACD Cross")
    st.write(macd_cross)

    st.subheader("كشف تجميع الحيتان 🐋")
    if whale_signal:
        st.success("يوجد احتمال تجميع حيتان")
    else:
        st.write("لا يوجد تجميع واضح")

    st.subheader("Volume Profile")
    st.bar_chart(vp.set_index("Price Range"))

    st.subheader("Score قوة العملة")
    st.write(f"{score} / 11")

    st.subheader("أفضل نقطة شراء")
    st.write(round(buy_zone,4))

    st.subheader("الهدف القريب")
    st.write(round(target,4))

    st.subheader("وقف الخسارة")
    st.write(round(stop_loss,4))

    st.subheader("توقع الحركة القادمة")
    st.write(prediction)

    st.subheader("نسبة نجاح الصفقة %")
    st.write(f"{success_rate:.1f} %")
