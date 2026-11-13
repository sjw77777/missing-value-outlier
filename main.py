import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="건물 에너지 데이터 - 전처리 및 EDA 앱",
    page_icon="🧹",
    layout="wide",
)

# 한글 폰트 및 마이너스 기호 깨짐 방지
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

st.title('🧹 건물 에너지 데이터 전처리 및 탐색적 분석(EDA) 웹앱')
st.write(
    '결측치 확인, IQR 이상치 정제, 그리고 독립변수 9개를 선정하기 위한 시각화(산점도,'
    ' 막대그래프, 히트맵)를 수행합니다.'
)


@st.cache_data
def load_data():
  return pd.read_csv('Energy_consumption.csv')


try:
  df = load_data()
  num_cols = [
      'Temperature',
      'Humidity',
      'SquareFootage',
      'Occupancy',
      'EnergyConsumption',
  ]
  cat_cols = ['HVACUsage', 'LightingUsage', 'DayOfWeek', 'Holiday']

  # =====================================================================
  # 1단계: 결측치 확인
  # =====================================================================
  st.header('1단계: 결측치(Missing Value) 확인')
  null_counts = df.isnull().sum().reset_index()
  null_counts.columns = ['컬럼명', '결측치 개수']
  total_nulls = df.isnull().sum().sum()

  st.dataframe(null_counts, use_container_width=True)
  st.info(f'💡 데이터셋 내 총 결측치 개수는 **{total_nulls}개**입니다.')

  st.markdown('---')

  # =====================================================================
  # 2단계: 이상치 분석 및 Boxplot 시각화
  # =====================================================================
  st.header('2단계: 이상치(Outlier) 분석 및 상자 그림(Boxplot)')
  outlier_counts = {}
  total_outliers = 0

  for col in num_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    cnt = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
    outlier_counts[col] = cnt
    total_outliers += cnt

  outlier_df = pd.DataFrame(
      list(outlier_counts.items()), columns=['컬럼명', '이상치 개수']
  )

  col1, col2 = st.columns([2, 1])
  with col1:
    st.dataframe(outlier_df, use_container_width=True)
  with col2:
    st.info(f'📌 **총 이상치 개수**: **{total_outliers}개**')

  st.subheader('📦 수치형 변수 Boxplot 시각화')
  fig, ax = plt.subplots(figsize=(10, 4))
  sns.boxplot(
      data=df[['Temperature', 'Humidity', 'Occupancy']], ax=ax, palette='Set2'
  )
  st.pyplot(fig)

  st.markdown('---')

  # =====================================================================
  # 3단계: 이상치 정제(클리핑) 및 파일 다운로드
  # =====================================================================
  st.header('3단계: 이상치 정제(클리핑) 및 정제 파일 생성')
  df_processed = df.copy()
  for col in num_cols:
    Q1 = df_processed[col].quantile(0.25)
    Q3 = df_processed[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df_processed[col] = np.clip(df_processed[col], lower_bound, upper_bound)

  st.success('🎉 IQR 클리핑을 통한 이상치 정제가 완료되었습니다!')

  csv_data = df_processed.to_csv(index=False).encode('utf-8-sig')
  st.download_button(
      label='📥 정제된 데이터(Energy_consumption_cleaned.csv) 다운로드',
      data=csv_data,
      file_name='Energy_consumption_cleaned.csv',
      mime='text/csv',
  )

  st.markdown('---')

  # =====================================================================
  # 4단계: 탐색적 데이터 분석(EDA) 및 독립변수 선정 근거 시각화
  # =====================================================================
  st.header(
      '4단계: 탐색적 데이터 분석(EDA) 및 독립변수(9개) 선정 근거 시각화'
  )
  st.write(
      '정제된 데이터를 바탕으로, 왜 이 수치형·범주형 변수들을 독립변수로'
      ' 채택했는지 시각화로 증명합니다.'
  )

  # 1. 수치형 관계 (산점도 + 추세선)
  st.subheader('📈 1) 수치형 변수와 에너지 소비량의 관계 (산점도)')
  col3, col4 = st.columns(2)
  with col3:
    st.write('**건물 면적 vs 에너지 소비량**')
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(
        data=df_processed,
        x='SquareFootage',
        y='EnergyConsumption',
        hue='Occupancy',
        palette='viridis',
        ax=ax,
        alpha=0.7,
    )
    sns.regplot(
        data=df_processed,
        x='SquareFootage',
        y='EnergyConsumption',
        scatter=False,
        ax=ax,
        color='red',
    )
    st.pyplot(fig)
    st.info('💡 면적이 넓을수록 에너지가 비례해서 증가하는 뚜렷한 양의 상관관계')

  with col4:
    st.write('**온도 vs 에너지 소비량**')
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(
        data=df_processed,
        x='Temperature',
        y='EnergyConsumption',
        hue='Humidity',
        palette='coolwarm',
        ax=ax,
        alpha=0.7,
    )
    sns.regplot(
        data=df_processed,
        x='Temperature',
        y='EnergyConsumption',
        scatter=False,
        ax=ax,
        color='blue',
    )
    st.pyplot(fig)
    st.info('💡 기온 변화에 따른 냉난방 부하(에너지 변동) 확인')

  # 2. 범주형 관계 (막대그래프)
  st.subheader('📊 2) 범주형 설비/일정 조건별 평균 에너지 소비량 (막대그래프)')
  col5, col6 = st.columns(2)
  with col5:
    st.write('**냉난방기 가동 여부별 평균 에너지**')
    fig, ax = plt.subplots(figsize=(6, 4))
    hvac_mean = (
        df_processed.groupby('HVACUsage')['EnergyConsumption']
        .mean()
        .reset_index()
    )
    sns.barplot(
        data=hvac_mean, x='HVACUsage', y='EnergyConsumption', palette='Set2', ax=ax
    )
    st.pyplot(fig)
    st.info('💡 냉난방기 가동 유무에 따라 에너지 소비량에 확연한 차이 발생')

  with col6:
    st.write('**휴일 여부별 평균 에너지**')
    fig, ax = plt.subplots(figsize=(6, 4))
    holiday_mean = (
        df_processed.groupby('Holiday')['EnergyConsumption'].mean().reset_index()
    )
    sns.barplot(
        data=holiday_mean,
        x='Holiday',
        y='EnergyConsumption',
        palette='Pastel1',
        ax=ax,
    )
    st.pyplot(fig)
    st.info('💡 휴일에 따른 상주 인원 및 패턴 변화 반영')

  # 3. 종합 히트맵
  st.subheader('🔥 3) 수치형 변수 종합 상관관계 히트맵')
  fig, ax = plt.subplots(figsize=(8, 4))
  sns.heatmap(
      df_processed[num_cols].corr(),
      annot=True,
      cmap='coolwarm',
      fmt='.2f',
      ax=ax,
      linewidths=0.5,
  )
  st.pyplot(fig)

except FileNotFoundError:
  st.error(
      "⚠️ 'Energy_consumption.csv' 파일을 찾을 수 없습니다. 폴더 위치를"
      ' 확인해주세요.'
  )
