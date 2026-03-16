import streamlit as st
import requests
import pandas as pd
import urllib.parse
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

st.set_page_config(page_title="물리치료 EBP 검색기", page_icon="🏥", layout="wide")

st.markdown('''
<style>
.custom-table {width: 100%; border-collapse: collapse; font-size: 14px; text-align: left;}
.custom-table th, .custom-table td {border: 1px solid #e0e0e0; padding: 12px;}
.custom-table th {background-color: #f8f9fa; font-weight: bold;}
.custom-table tr:hover {background-color: #f1f3f5;}
.hover-title {border-bottom: 2px dashed #4CAF50; cursor: help; color: #1f77b4; font-weight: bold;}
.ai-link-button {
    display: inline-block;
    padding: 10px 20px;
    margin: 5px;
    background-color: #f0f2f6;
    border-radius: 10px;
    text-decoration: none;
    color: #31333F !important;
    font-weight: bold;
    border: 1px solid #d1d5db;
}
.ai-link-button:hover { background-color: #e0e4ea; }
</style>
''', unsafe_allow_html=True)

st.title("🏥 EBP 종합 논문 검색기")
st.markdown("한글 검색어 입력 시 **자동으로 영어로 번역**하여 전 세계 논문을 동시에 찾아줍니다!")

with st.sidebar:
    st.header("🔍 검색어 조합 설정 (한/영 모두 가능)")
    
    st.markdown("**1. 첫 번째 검색어 (필수)**")
    keyword1 = st.text_input("ex) 뇌졸중", value="뇌졸중", label_visibility="collapsed")
    
    col1_1, col1_2 = st.columns([1, 2.5])
    with col1_1: cond1 = st.selectbox("조건 1", ["AND", "OR", "NOT"], key="c1")
    with col1_2: keyword2 = st.text_input("두 번째 검색어 (선택)", value="물리치료")
        
    col2_1, col2_2 = st.columns([1, 2.5])
    with col2_1: cond2 = st.selectbox("조건 2", ["AND", "OR", "NOT"], key="c2")
    with col2_2: keyword3 = st.text_input("세 번째 검색어 (선택)", value="재활")
        
    k1, k2, k3 = keyword1.strip(), keyword2.strip(), keyword3.strip()
    
    if k2 and k3: final_keyword_kr = f"(({k1}) {cond1} ({k2})) {cond2} ({k3})"
    elif k2: final_keyword_kr = f"({k1}) {cond1} ({k2})"
    elif k3: final_keyword_kr = f"({k1}) {cond2} ({k3})"
    else: final_keyword_kr = f"({k1})"
        
    st.info(f"💡 원본 검색식: \n{final_keyword_kr}")
    
    st.markdown("---")
    st.header("📚 검색 대상 DB 선택")
    db_pubmed = st.checkbox("🟢 PubMed", value=True)
    db_cochrane = st.checkbox("🔵 Cochrane Library", value=True)
    db_scholar = st.checkbox("🎓 Google Scholar", value=True)
    db_riss = st.checkbox("🇰🇷 RISS", value=True)
    db_kiss = st.checkbox("🇰🇷 KISS", value=True)
    
    st.markdown("---")
    st.header("📄 논문 유형 (PubMed)")
    type_rct = st.checkbox("RCT", value=True)
    type_cpg = st.checkbox("CPGs", value=True)
    type_sr = st.checkbox("SR", value=True)
    
    st.markdown("---")
    start_year = st.number_input("출판 연도 시작", min_value=1990, max_value=2026, value=2020)
    max_results = st.slider("최대 표출 갯수", 5, 20, 5, 5)
    search_button = st.button("검색 실행 🚀")

if search_button and k1:
    translator_ko_to_en = GoogleTranslator(source='auto', target='en')
    translator_en_to_ko = GoogleTranslator(source='en', target='ko')
    
    with st.spinner("검색어를 영어로 자동 번역 중입니다..."):
        try:
            k1_en = translator_ko_to_en.translate(k1)
            k2_en = translator_ko_to_en.translate(k2) if k2 else ""
            k3_en = translator_ko_to_en.translate(k3) if k3 else ""
            
            if k2_en and k3_en: final_keyword_en = f"(({k1_en}) {cond1} ({k2
