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


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 페이지 설정
st.set_page_config(
    page_title="건물 에너지 데이터 - 이상치 확인",
    page_icon="📊",
    layout="wide"
)

st.title("📊 건물 에너지 데이터 전처리 - 2단계: 이상치 확인")
st.write("IQR(사분위수 범위) 공식을 사용하여 각 변수별 이상치가 정확히 몇 개인지 수치로 확인합니다.")

# 데이터 불러오기
@st.cache_data
def load_data():
    return pd.read_csv('Energy_consumption.csv')

try:
    df = load_data()
    num_cols = ['Temperature', 'Humidity', 'SquareFootage', 'Occupancy', 'EnergyConsumption']

    # 1. IQR 기준으로 컬럼별 이상치 개수 정확히 계산하기
    outlier_counts = {}
    total_outliers = 0

    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 정상 범위를 벗어나는 데이터 개수 구하기
        cond = (df[col] < lower_bound) | (df[col] > upper_bound)
        cnt = cond.sum()
        outlier_counts[col] = cnt
        total_outliers += cnt

    # 표 형태로 변환
    outlier_df = pd.DataFrame(list(outlier_counts.items()), columns=['컬럼명', '이상치 개수'])

    # 2. 화면 출력 (표 + 안내 박스)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📋 컬럼별 이상치 개수 현황 표")
        st.dataframe(outlier_df, use_container_width=True)
    with col2:
        st.subheader("💡 요약 안내")
        st.info(f"**전체 데이터 행 수**: {len(df)}개\n\n**총 이상치 개수**: **{total_outliers}개**")

    # 3. 기술 통계량 표 (describe)
    st.subheader("📈 주요 수치형 변수 통계 요약 표")
    st.dataframe(df[num_cols].describe(), use_container_width=True)

    # 4. 상자 그림(Boxplot) 시각화 출력
    st.subheader("📦 주요 변수 상자 그림 (Boxplot)")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.boxplot(data=df[['Temperature', 'Humidity', 'Occupancy']], ax=ax, palette="Set2")
    plt.title("Boxplot for Outlier Detection")
    st.pyplot(fig)

except FileNotFoundError:
    st.error("⚠️ 'Energy_consumption.csv' 파일을 찾을 수 없습니다. 동일한 폴더에 파일이 위치해 있는지 확인해 주세요.")
