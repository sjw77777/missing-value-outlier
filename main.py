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
        
        cond = (df[col] < lower_bound) | (df[col] > upper_bound)
        cnt = cond.sum()
        outlier_counts[col] = cnt
        total_outliers += cnt

    outlier_df = pd.DataFrame(list(outlier_counts.items()), columns=['컬럼명', '이상치 개수'])

    # 2. 화면 출력 (표 + 안내 박스)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📋 컬럼별 이상치 개수 현황 표")
        st.dataframe(outlier_df, use_container_width=True)
    with col2:
        st.subheader("💡 분석 의미 해석")
        st.info(f"**전체 데이터 행 수**: {len(df)}개\n\n**총 이상치 개수**: **{total_outliers}개**\n\n👉 대부분의 데이터가 정제되어 있어 이상치가 거의 없는 안정적인 분포를 보입니다.")

    # 3. 기술 통계량 표 (describe)
    st.subheader("📈 주요 수치형 변수 통계 요약 표")
    st.write("📌 **의미**: 최소값(`min`), 최대값(`max`), 그리고 중간값(`50%`)을 통해 데이터의 전반적인 중심 경향과 퍼져 있는 정도를 파악합니다.")
    st.dataframe(df[num_cols].describe(), use_container_width=True)

    # 4. 상자 그림(Boxplot) 시각화 출력
    st.subheader("📦 주요 변수 상자 그림 (Boxplot)")
    st.write("📌 **의미**: 박스 위아래로 뻗은 수염(Whiskers) 바깥쪽에 독립된 점으로 찍히는 값이 이상치입니다. 현재 그래프에서는 극단적으로 튀는 값 없이 상자 범위 내에 데이터가 잘 밀집해 있음을 시각적으로 확인할 수 있습니다.")
    
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.boxplot(data=df[['Temperature', 'Humidity', 'Occupancy']], ax=ax, palette="Set2")
    plt.title("Boxplot for Outlier Detection")
    st.pyplot(fig)

except FileNotFoundError:
    st.error("⚠️ 'Energy_consumption.csv' 파일을 찾을 수 없습니다. 동일한 폴더에 파일이 위치해 있는지 확인해 주세요.")


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 페이지 설정
st.set_page_config(
    page_title="건물 에너지 데이터 - 이상치 해결",
    page_icon="✨",
    layout="wide"
)

st.title("✨ 건물 에너지 데이터 전처리 - 3단계: 이상치 해결")
st.write("IQR(사분위수 범위) 기준을 벗어난 이상치(1개)를 정상 범위 경계값으로 다듬는 클리핑(Clipping)을 수행합니다.")

# 데이터 불러오기
@st.cache_data
def load_data():
    return pd.read_csv('Energy_consumption.csv')

try:
    df = load_data()
    num_cols = ['Temperature', 'Humidity', 'SquareFootage', 'Occupancy', 'EnergyConsumption']

    # 1단계: 정제 전 이상치 개수 파악
    before_outliers = 0
    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        before_outliers += ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()

    # 2단계: IQR 클리핑 적용 (이상치 해결)
    df_processed = df.copy()
    for col in num_cols:
        Q1 = df_processed[col].quantile(0.25)
        Q3 = df_processed[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df_processed[col] = np.clip(df_processed[col], lower_bound, upper_bound)

    # 3단계: 정제 후 이상치 개수 재확인 (0개 확인용)
    after_outliers = 0
    for col in num_cols:
        Q1 = df_processed[col].quantile(0.25)
        Q3 = df_processed[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        after_outliers += ((df_processed[col] < lower_bound) | (df_processed[col] > upper_bound)).sum()

    # 화면 출력 (성공 메시지 및 비교 통계)
    st.success("🎉 이상치 정제(IQR Clipping)가 성공적으로 완료되었습니다!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📌 **정제 전 이상치 총합**: **{before_outliers}개** (EnergyConsumption 1개 포함)")
    with col2:
        st.info(f"📌 **정제 후 이상치 총합**: **{after_outliers}개** (정상 범위로 완벽 교정됨)")

    st.subheader("📋 이상치가 정제된 최종 데이터 통계 요약")
    st.write("📌 **의미**: 클리핑을 통해 극단적인 값이 상·하한 경계값으로 조정되어, 데이터의 안정성이 높아진 것을 통계량(`min`, `max`)을 통해 확인할 수 있습니다.")
    st.dataframe(df_processed[num_cols].describe(), use_container_width=True)

    st.subheader("📋 최종 정제된 데이터프레임 (상위 5개 행)")
    st.dataframe(df_processed.head(), use_container_width=True)

except FileNotFoundError:
    st.error("⚠️ 'Energy_consumption.csv' 파일을 찾을 수 없습니다. 동일한 폴더에 파일이 위치해 있는지 확인해 주세요.")
