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
            
            if k2_en and k3_en: final_keyword_en = f"(({k1_en}) {cond1} ({k2_en})) {cond2} ({k3_en})"
            elif k2_en: final_keyword_en = f"({k1_en}) {cond1} ({k2_en})"
            elif k3_en: final_keyword_en = f"({k1_en}) {cond2} ({k3_en})"
            else: final_keyword_en = f"({k1_en})"
            
            st.success(f"🔤 번역된 영어 검색식: **{final_keyword_en}**")
        except Exception as e:
            final_keyword_en = final_keyword_kr
            st.warning("검색어 번역에 실패하여 원본 검색어로 진행합니다.")

    st.subheader("🔗 국내/외부 데이터베이스 다이렉트 검색")
    
    safe_kws = [k for k in [k1, k2, k3] if k]
    safe_keyword_kr = " ".join(safe_kws)
    encoded_safe_kr = urllib.parse.quote(safe_keyword_kr)
    
    encoded_kw_kr = urllib.parse.quote(final_keyword_kr)
    
    l_col1, l_col2, l_col3 = st.columns(3)
    if db_scholar: l_col1.markdown(f"[🎓 구글 스칼라 검색](https://scholar.google.com/scholar?q={encoded_kw_kr})")
    if db_riss: l_col2.markdown(f"[🇰🇷 RISS 통합검색](http://www.riss.kr/search/Search.do?isDetailSearch=N&searchGubun=true&viewYn=OP&query={encoded_safe_kr})")
    
    # 💡 [핵심 해결] KISS 철벽 방어 우회: 홈페이지 이동 + 복사 버튼 제공
    if db_kiss: l_col3.markdown(f"[🇰🇷 KISS 홈페이지로 가기](https://kiss.kstudy.com/)")
    
    st.divider()
    
    if db_kiss:
        st.caption("🚨 **KISS 검색 안내:** KISS의 외부 검색 차단 정책으로 인해 다이렉트 연결이 불가능합니다. 아래 박스 우측 상단의 📋 버튼을 눌러 검색어를 복사한 뒤, KISS 홈페이지 검색창에 직접 붙여넣어 주세요.")
        st.code(safe_keyword_kr, language="text")

    papers = []
    if db_pubmed or db_cochrane:
        with st.spinner("해외 논문을 분석하고 한글로 요약 번역 중입니다..."):
            try:
                cochrane_ids, pubmed_ids = [], []
                if db_cochrane:
                    c_term = f"({final_keyword_en}) AND \"Cochrane Database Syst Rev\"[Journal]"
                    url_c = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={c_term}&retmode=json&retmax={max_results}&mindate={start_year}&maxdate=2026&datetype=pdat"
                    cochrane_ids = requests.get(url_c).json().get('esearchresult', {}).get('idlist', [])
                if db_pubmed:
                    types = []
                    if type_rct: types.append("randomized controlled trial[Publication Type]")
                    if type_cpg: types.append("practice guideline[Publication Type]")
                    if type_sr: types.append("systematic review[Publication Type]")
                    t_query = " OR ".join(types) if types else "journal article[Publication Type]"
                    p_term = f"({final_keyword_en}) AND ({t_query}) NOT \"Cochrane Database Syst Rev\"[Journal]"
                    url_p = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={p_term}&retmode=json&retmax={max_results}&mindate={start_year}&maxdate=2026&datetype=pdat"
                    pubmed_ids = requests.get(url_p).json().get('esearchresult', {}).get('idlist', [])

                all_ids = cochrane_ids + pubmed_ids
                if all_ids:
                    f_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(all_ids)}&retmode=xml"
                    soup = BeautifulSoup(requests.get(f_url).content, 'xml')
                    for art in soup.find_all('PubmedArticle'):
                        pmid = art.find('PMID').text if art.find('PMID') else ""
                        title = art.find('ArticleTitle').text if art.find('ArticleTitle') else "제목 없음"
                        jrnl = art.find('Title').text if art.find('Title') else ""
                        yr = art.find('PubDate').find('Year').text if art.find('PubDate') and art.find('PubDate').find('Year') else "미상"
                        
                        abs_txts = art.find_all('AbstractText')
                        summ_en, full_abs = "", ""
                        for ab in abs_txts:
                            lbl = ab.get('Label', '').upper()
                            txt = ab.text.strip()
                            full_abs += txt + " "
                            if 'CONCLUSION' in lbl or 'RESULT' in lbl: summ_en += txt + " "
                        if not summ_en: summ_en = full_abs[-500:]

                        try: kt, ks = translator_en_to_ko.translate(title), translator_en_to_ko.translate(summ_en)
                        except: kt, ks = "번역 실패", "번역 실패"

                        tooltip = f"[제목 번역]\n{kt}\n\n[초록 요약]\n{ks}".replace('"', '&quot;').replace('\n', '&#10;')
                        t_html = f'<span class="hover-title" title="{tooltip}">{title}</span>'
                        
                        pmc_id = ""
                        for aid in art.find_all('ArticleId'):
                            if aid.get('IdType') == 'pmc': pmc_id = aid.text
                        l_html = f'<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/" target="_blank">🔓 무료 PDF</a>' if pmc_id else f'<a href="https://pubmed.ncbi.nlm.nih.gov/{pmid}/" target="_blank">🔗 원문 링크</a>'
                        
                        src = "🔵 Cochrane" if "Cochrane" in jrnl else "🟢 PubMed"
                        papers.append({"출처": src, "연도": yr, "논문 제목 (마우스 오버)": t_html, "링크": l_html})
            except Exception as e: st.error(f"오류: {e}")

        if papers:
            st.markdown("### 📊 해외 논문 분석 결과")
            st.markdown(pd.DataFrame(papers).to_html(escape=False, index=False, classes="custom-table"), unsafe_allow_html=True)
            st.success(f"🎉 {len(papers)}개의 해외 논문을 찾고 한글 번역을 완료했습니다!")

    st.divider()
    st.markdown("### 🚀 더 전문적인 분석을 위한 AI 도구 바로가기")
    st.markdown('''
        <div style="display: flex; justify-content: flex-start; flex-wrap: wrap;">
            <a href="https://typeset.io/" target="_blank" class="ai-link-button">🌐 SciSpace (한글 요약/채팅)</a>
            <a href="https://elicit.com/" target="_blank" class="ai-link-button">🔍 Elicit (연구 질문 분석)</a>
            <a href="https://consensus.app/" target="_blank" class="ai-link-button">🤝 Consensus (학계 합의 확인)</a>
            <a href="https://www.chatpdf.com/" target="_blank" class="ai-link-button">💬 ChatPDF (PDF 대화 분석)</a>
            <a href="https://www.deepl.com/translator" target="_blank" class="ai-link-button">📝 DeepL (최강 파일 번역기)</a>
        </div>
    ''', unsafe_allow_html=True)
