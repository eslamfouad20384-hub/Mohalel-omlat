import streamlit as st
import requests
import pandas as pd
import numpy as np
import ta

# =========================
# إعداد الصفحة والخطوط
# =========================
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    .big-font { font-size:20px !important; }
    .title-font { font-size:32px !important; font-weight:bold; color:#0b3d91; }
    .success { color: green; font-weight:bold; }
    .error { color: red; font-weight:bold; }
    .warning { color: orange; font-weight:bold; }
    </style>
    """, unsafe_allow_html=True
)
st.markdown('<p class="title-font">Crypto Full Analyzer PRO – التقرير الشامل</p>', unsafe_allow_html=True)

API_KEY = "ضع_مفتاحك"
coin = st.text_input("اكتب رمز العملة مثل BTC أو DOT").upper()

if coin:
    status = st.empty()  # عنصر لتحديث حالة كل خطوة

    # -----------------------
    # جلب البيانات
    # -----------------------
    status.write("🚀 جلب البيانات...")
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={coin}&tsym=USD&limit=365&api_key={API_KEY}"
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
    # مؤشرات فنية محسّنة
    # -----------------------
    status.write("📊 حساب المؤشرات الفنية...")
    try:
        # EMA
        df["EMA20"] = ta.trend.ema_indicator(df["close"], window=20)
        df["EMA50"] = ta.trend.ema_indicator(df["close"], window=50)
        df["EMA200"] = ta.trend.ema_indicator(df["close"], window=200)
        # RSI
        rsi_indicator = ta.momentum.RSIIndicator(df["close"])
        df["RSI"] = rsi_indicator.rsi()
        # MACD
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
    # فيبوناتشي
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
    # Volume Profile محسّن
    # -----------------------
    status.write("📊 حساب Volume Profile...")
    try:
        bins = np.linspace(df["low"].min(), df["high"].max(), 50)  # bins أكبر وديناميكي
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
    # حساب Score محسّن
    # -----------------------
    status.write("📝 حساب Score وقوة العملة...")
    try:
        rsi = df["RSI"].iloc[-1]
        score = 0
        weights = 0

        # مثال أوزان ديناميكية
        if rsi < 35: score += 2; weights += 2
        elif rsi < 55: score += 1; weights += 1
        if ema_signal == "تقاطع صعودي 🚀": score += 3; weights +=3
        if macd_cross == "تقاطع صعودي 📈": score += 2; weights +=2
        if whale_signal: score += 3; weights +=3
        if df["close"].iloc[-1] < fib_levels["0.5"]: score += 1; weights +=1

        score_percent = (score / weights) * 100 if weights > 0 else 0
        status.success(f"✅ Score: {score} / {weights} ({score_percent:.1f}%)")
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
    # عرض النتائج النهائية منسقة وملونة
    # -----------------------
    st.markdown('<hr>', unsafe_allow_html=True)
    st.subheader("🖌 النتائج النهائية", anchor=None)

    st.markdown(f'<p class="big-font">السعر الحالي: {df["close"].iloc[-1]:.4f}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="big-font">الدعم: {support:.4f} | المقاومة: {resistance:.4f}</p>', unsafe_allow_html=True)
    st.markdown('<p class="big-font">مستويات فيبوناتشي:</p>', unsafe_allow_html=True)
    for k,v in fib_levels.items():
        st.markdown(f'<p class="big-font">{k}: {v:.4f}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="big-font">EMA Cross: {ema_signal}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="big-font">MACD Cross: {macd_cross}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="big-font">حالة تجميع الحيتان: {"يوجد احتمال تجميع" if whale_signal else "لا يوجد تجميع"}</p>', unsafe_allow_html=True)

    st.markdown('<p class="big-font">Volume Profile:</p>', unsafe_allow_html=True)
    st.bar_chart(vp.set_index("Price Range"))

    st.markdown(f'<p class="big-font">Score: {score} / {weights} ({score_percent:.1f}%)</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="big-font">أفضل نقطة شراء: {round(buy_zone,4)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="big-font">الهدف: {round(target,4)} | وقف الخسارة: {round(stop_loss,4)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="big-font">توقع الحركة القادمة: {prediction}</p>', unsafe_allow_html=True)
