import streamlit as st
import requests
import pandas as pd
import numpy as np
import ta

st.set_page_config(layout="wide")
st.title("Crypto Full Analyzer PRO – مع متابعة كل خطوة")

API_KEY = "ضع_مفتاحك"
coin = st.text_input("اكتب رمز العملة مثل BTC أو DOT").upper()

if coin:
    status = st.empty()  # عنصر لتحديث حالة كل خطوة

    # -----------------------
    # جلب البيانات
    # -----------------------
    status.write("🚀 جلب البيانات...")
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={coin}&tsym=USD&limit=120&api_key={API_KEY}"
        data = requests.get(url).json()
        data_list = data.get("Data", {}).get("Data", [])
        if not data_list:
            status.error("❌ لا توجد بيانات")
            st.stop()
        status.success("✅ تم جلب البيانات بنجاح")
    except Exception as e:
        status.error(f"❌ خطأ أثناء جلب البيانات: {e}")
        st.stop()

    # -----------------------
    # تحويل البيانات
    # -----------------------
    status.write("🔄 تحويل البيانات لـ DataFrame...")
    try:
        df = pd.DataFrame(data_list)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df["volume"] = df["volumeto"]
        status.success("✅ تم التحويل بنجاح")
    except Exception as e:
        status.error(f"❌ خطأ أثناء التحويل: {e}")
        st.stop()

    # -----------------------
    # حساب المؤشرات الفنية
    # -----------------------
    status.write("📊 حساب المؤشرات الفنية...")
    try:
        df["EMA20"] = ta.trend.ema_indicator(df["close"], window=20)
        df["EMA50"] = ta.trend.ema_indicator(df["close"], window=50)
        df["EMA200"] = ta.trend.ema_indicator(df["close"], window=200)

        rsi_indicator = ta.momentum.RSIIndicator(df["close"])
        df["RSI"] = rsi_indicator.rsi()

        macd_indicator = ta.trend.MACD(df["close"])
        df["MACD"] = macd_indicator.macd()
        df["MACD_signal"] = macd_indicator.macd_signal()
        status.success("✅ تم حساب المؤشرات الفنية")
    except Exception as e:
        status.error(f"❌ خطأ أثناء حساب المؤشرات: {e}")
        st.stop()

    # -----------------------
    # الدعم والمقاومة
    # -----------------------
    status.write("📌 حساب الدعم والمقاومة...")
    try:
        support = df["low"].tail(20).min()
        resistance = df["high"].tail(20).max()
        status.success("✅ تم حساب الدعم والمقاومة")
    except Exception as e:
        status.error(f"❌ خطأ في حساب الدعم والمقاومة: {e}")
        st.stop()

    # -----------------------
    # مستويات فيبوناتشي
    # -----------------------
    status.write("📈 حساب مستويات فيبوناتشي...")
    try:
        high = df["high"].max()
        low = df["low"].min()
        fib_levels = {
            "0.236": high - (high-low)*0.236,
            "0.382": high - (high-low)*0.382,
            "0.5": high - (high-low)*0.5,
            "0.618": high - (high-low)*0.618
        }
        status.success("✅ تم حساب مستويات فيبوناتشي")
    except Exception as e:
        status.error(f"❌ خطأ في حساب فيبوناتشي: {e}")
        st.stop()

    # -----------------------
    # EMA Cross
    # -----------------------
    status.write("🔀 فحص تقاطع EMA...")
    try:
        ema_signal = "محايد"
        if df["EMA20"].iloc[-2] < df["EMA50"].iloc[-2] and df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]:
            ema_signal = "تقاطع صعودي 🚀"
        if df["EMA20"].iloc[-2] > df["EMA50"].iloc[-2] and df["EMA20"].iloc[-1] < df["EMA50"].iloc[-1]:
            ema_signal = "تقاطع هبوطي"
        status.success(f"✅ EMA Cross: {ema_signal}")
    except Exception as e:
        status.error(f"❌ خطأ في EMA Cross: {e}")
        st.stop()

    # -----------------------
    # MACD Cross
    # -----------------------
    status.write("🔀 فحص تقاطع MACD...")
    try:
        macd_cross = "محايد"
        if df["MACD"].iloc[-2] < df["MACD_signal"].iloc[-2] and df["MACD"].iloc[-1] > df["MACD_signal"].iloc[-1]:
            macd_cross = "تقاطع صعودي 📈"
        if df["MACD"].iloc[-2] > df["MACD_signal"].iloc[-2] and df["MACD"].iloc[-1] < df["MACD_signal"].iloc[-1]:
            macd_cross = "تقاطع هبوطي"
        status.success(f"✅ MACD Cross: {macd_cross}")
    except Exception as e:
        status.error(f"❌ خطأ في MACD Cross: {e}")
        st.stop()

    # -----------------------
    # كشف تجميع الحيتان
    # -----------------------
    status.write("🐋 فحص تجميع الحيتان...")
    try:
        avg_volume = df["volume"].tail(30).mean()
        current_volume = df["volume"].iloc[-1]
        price_change = abs(df["close"].iloc[-1] - df["close"].iloc[-5]) / df["close"].iloc[-5]
        whale_signal = current_volume > avg_volume * 2 and price_change < 0.04
        status.success(f"✅ فحص الحيتان: {'يوجد احتمال تجميع' if whale_signal else 'لا يوجد تجميع'}")
    except Exception as e:
        status.error(f"❌ خطأ في فحص الحيتان: {e}")
        st.stop()

    # -----------------------
    # Volume Profile
    # -----------------------
    status.write("📊 حساب Volume Profile...")
    try:
        bins = np.linspace(df["low"].min(), df["high"].max(), 24)
        df["price_bin"] = pd.cut(df["close"], bins)
        vp = df.groupby("price_bin")["volume"].sum().reset_index()
        vp["range"] = vp["price_bin"].apply(lambda x: f"{x.left:.2f}-{x.right:.2f}")
        vp = vp[["range","volume"]]
        vp.columns = ["Price Range","Volume"]
        status.success("✅ تم حساب Volume Profile")
    except Exception as e:
        status.error(f"❌ خطأ في Volume Profile: {e}")
        st.stop()

    # -----------------------
    # حساب Score
    # -----------------------
    status.write("📝 حساب Score وقوة العملة...")
    try:
        rsi = df["RSI"].iloc[-1]
        score = 0
        if rsi < 35: score += 2
        elif rsi < 55: score += 1
        if ema_signal == "تقاطع صعودي 🚀": score += 3
        if macd_cross == "تقاطع صعودي 📈": score += 2
        if whale_signal: score += 3
        if df["close"].iloc[-1] < fib_levels["0.5"]: score += 1
        status.success(f"✅ Score: {score} / 11")
    except Exception as e:
        status.error(f"❌ خطأ في حساب Score: {e}")
        st.stop()

    # -----------------------
    # أفضل نقطة شراء
    # -----------------------
    status.write("💰 حساب أفضل نقطة شراء...")
    try:
        buy_zone = (support + fib_levels["0.618"]) / 2
        status.success(f"✅ أفضل نقطة شراء: {round(buy_zone,4)}")
    except Exception as e:
        status.error(f"❌ خطأ في حساب أفضل نقطة شراء: {e}")
        st.stop()

    # -----------------------
    # الهدف ووقف الخسارة
    # -----------------------
    status.write("🎯 حساب الهدف ووقف الخسارة...")
    try:
        target = resistance
        stop_loss = support * 0.97
        status.success(f"✅ الهدف: {round(target,4)}, وقف الخسارة: {round(stop_loss,4)}")
    except Exception as e:
        status.error(f"❌ خطأ في حساب الهدف ووقف الخسارة: {e}")
        st.stop()

    # -----------------------
    # توقع الحركة القادمة
    # -----------------------
    status.write("🔮 توقع الحركة القادمة...")
    try:
        trend_score = 0
        if rsi < 35: trend_score += 2
        elif rsi > 65: trend_score -= 2
        if ema_signal == "تقاطع صعودي 🚀": trend_score += 2
        elif ema_signal == "تقاطع هبوطي": trend_score -= 2
        if macd_cross == "تقاطع صعودي 📈": trend_score += 2
        elif macd_cross == "تقاطع هبوطي": trend_score -= 2
        if whale_signal: trend_score += 2

        if trend_score >= 3: prediction = "📈 احتمال صعود"
        elif trend_score <= -3: prediction = "📉 احتمال هبوط"
        else: prediction = "➡️ حركة عرضية"

        status.success(f"✅ توقع الحركة: {prediction}")
    except Exception as e:
        status.error(f"❌ خطأ في توقع الحركة: {e}")
        st.stop()

    # -----------------------
    # نسبة نجاح الصفقة
    # -----------------------
    status.write("📊 حساب نسبة نجاح الصفقة...")
    try:
        success_rate = (score / 11) * 100
        status.success(f"✅ نسبة نجاح الصفقة: {success_rate:.1f} %")
    except Exception as e:
        status.error(f"❌ خطأ في حساب نسبة النجاح: {e}")
        st.stop()

    # -----------------------
    # عرض النتائج النهائية
    # -----------------------
    st.subheader("النتائج النهائية")
    st.write("السعر الحالي:", df["close"].iloc[-1])
    st.write("الدعم:", support)
    st.write("المقاومة:", resistance)
    st.write("مستويات فيبوناتشي:", fib_levels)
    st.write("EMA Cross:", ema_signal)
    st.write("MACD Cross:", macd_cross)
    st.write("حالة تجميع الحيتان:", "يوجد احتمال تجميع" if whale_signal else "لا يوجد تجميع")
    st.bar_chart(vp.set_index("Price Range"))
    st.write("Score قوة العملة:", score)
    st.write("أفضل نقطة شراء:", round(buy_zone,4))
    st.write("الهدف:", round(target,4))
    st.write("وقف الخسارة:", round(stop_loss,4))
    st.write("توقع الحركة القادمة:", prediction)
    st.write("نسبة نجاح الصفقة %:", f"{success_rate:.1f} %")
