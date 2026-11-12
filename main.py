import streamlit as st
import pandas as pd

# 웹앱 제목 설정
st.title("⚡ 건물 에너지 데이터 전처리 - 1단계: 결측치 확인")
st.write("업로드된 'Energy_consumption.csv' 파일에서 결측치(빈칸)를 확인합니다.")

# 데이터 불러오기 (캐시 적용)
@st.cache_data
def load_data():
    return pd.read_csv('Energy_consumption.csv')

# 데이터 로드 시도
try:
    df = load_data()

    # 1. 각 컬럼별 결측치 개수 계산 및 표 형태(DataFrame)로 변환
    null_counts = df.isnull().sum().reset_index()
    null_counts.columns = ['컬럼명', '결측치 개수']

    # 2. 데이터셋 전체의 총 결측치 개수 계산
    total_nulls = df.isnull().sum().sum()

    # 3. 결과 출력
    st.subheader("📊 컬럼별 결측치 현황 표")
    st.dataframe(null_counts, use_container_width=True)

    # 4. 전체 총 결측치 개수를 st.info 파란색 안내 박스로 출력
    st.info(f"💡 데이터셋 내 총 결측치(빈칸) 개수는 **{total_nulls}개**입니다.")

except FileNotFoundError:
    st.error("⚠️ 'Energy_consumption.csv' 파일을 찾을 수 없습니다. 동일한 폴더에 파일이 위치해 있는지 확인해 주세요.")
