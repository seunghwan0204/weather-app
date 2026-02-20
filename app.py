import streamlit as st
import requests
import pandas as pd
from streamlit_js_eval import get_geolocation

# 1. 설정 및 API 키
API_KEY = st.secrets["WEATHER_API_KEY"]
BASE_URL = "http://api.weatherapi.com/v1/forecast.json"

st.set_page_config(page_title="Weather Dash", page_icon="🌤️", layout="centered")

# CSS로 UI 크기 미세 조정
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 1rem; }
    .stMetric { padding: 5px 10px; border-radius: 8px; background: #ffffff; border: 1px solid #eee; }
    .weather-card { padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 15px; border: 1px solid #ddd; }
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.3rem !important; }
    h3 { font-size: 1.1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 세션 상태 초기화
if "favorites" not in st.session_state:
    st.session_state.favorites = ["Seoul", "New York", "London"]
if "target_city" not in st.session_state:
    st.session_state.target_city = "Seoul"

# 2. 날씨 데이터 가져오기 함수
def get_weather(query):
    params = {"key": API_KEY, "q": query, "days": 1, "aqi": "no"}
    res = requests.get(BASE_URL, params=params)
    return res.json()

def get_emoji(condition_text):
    cond = condition_text.lower()
    if "sunny" in cond or "clear" in cond: return "☀️"
    if "cloudy" in cond or "overcast" in cond: return "☁️"
    if "rain" in cond or "drizzle" in cond: return "☔"
    if "snow" in cond or "sleet" in cond: return "☃️"
    return "🌡️"

# 3. 사이드바: 즐겨찾기 관리 (추가 및 삭제)
with st.sidebar:
    st.title("⭐ 즐겨찾기 관리")
    
    # 추가 섹션
    new_city = st.text_input("도시 추가 (영문)", key="add_input").strip()
    if st.button("목록에 추가", use_container_width=True):
        if new_city and new_city not in st.session_state.favorites:
            st.session_state.favorites.append(new_city)
            st.rerun()

    st.divider()
    
    # 삭제 및 선택 섹션
    st.write("📍 **내 목록 (클릭 시 이동)**")
    for city in st.session_state.favorites:
        cols = st.columns([4, 1])
        if cols[0].button(f"🏙️ {city}", key=f"sel_{city}", use_container_width=True):
            st.session_state.target_city = city
            st.rerun()
        if cols[1].button("🗑️", key=f"del_{city}"):
            st.session_state.favorites.remove(city)
            if st.session_state.target_city == city:
                st.session_state.target_city = "Seoul"
            st.rerun()

# 4. 메인 화면
st.title("🌍 Mini Weather")

c1, c2 = st.columns([4, 1])
with c1:
    search_query = st.text_input("Search", value=st.session_state.target_city, label_visibility="collapsed")
with c2:
    if st.button("📍 GPS", use_container_width=True):
        loc = get_geolocation()
        if loc:
            search_query = f"{loc['coords']['latitude']},{loc['coords']['longitude']}"

# 데이터 렌더링
data = get_weather(search_query)

if "error" not in data:
    curr = data['current']
    loc_info = data['location']
    cast = data['forecast']['forecastday'][0]
    temp = curr['temp_c']
    
    # 배경색 결정
    bg = "#FFF9C4" if temp >= 30 else "#E1F5FE"
    emoji = get_emoji(curr['condition']['text'])

    # 메인 카드 (크기 대폭 축소)
    st.markdown(f"""
        <div class="weather-card" style="background-color:{bg};">
            <h2 style="margin:0;">{loc_info['name']}</h2>
            <div style="font-size: 50px; margin: 5px 0;">{emoji} {temp}°C</div>
            <p style="margin:0; font-weight:bold; color:#666;">{curr['condition']['text']}</p>
        </div>
    """, unsafe_allow_html=True)

    # 상세 정보 (가로로 조밀하게 배치)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("습도", f"{curr['humidity']}%")
    m2.metric("체감", f"{curr['feelslike_c']}°")
    m3.metric("UV", curr['uv'])
    m4.metric("달", cast['astro']['moon_phase'].split()[0]) # 이름만 짧게 표시

    # 가이드 (카드 형태로 작게)
    st.write("")
    g1, g2 = st.columns(2)
    with g1:
        st.caption("👔 **추천 복장**")
        msg = "반팔" if temp >= 25 else "긴팔" if temp >= 15 else "코트"
        st.write(f"{msg} 추천")
    with g2:
        st.caption("⚠️ **주의사항**")
        note = "우산 챙기세요" if "Rain" in curr['condition']['text'] else "자외선 주의" if curr['uv'] > 5 else "날씨 좋음"
        st.write(note)
else:
    st.error("도시를 찾을 수 없습니다.")