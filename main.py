import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="건물 에너지 데이터 - 전처리 및 9개 변수 EDA",
    page_icon="🧹",
    layout="wide",
)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

st.title('🧹 건물 에너지 데이터 전처리 및 독립변수(9개) 전수 EDA 웹앱')
st.write(
    '결측치 확인, 이상치 정제, 그리고 **독립변수 9개 전체**가 에너지 소비량과'
    ' 어떤 관계가 있는지 시각화로 철저하게 검증합니다.'
)


@st.cache_data
def load_data():
  return pd.read_csv('Energy_consumption.csv')


try:
  df = load_data()

  # 수치형 5개 (타겟인 EnergyConsumption 제외한 독립변수 4개 + 타겟 1개)
  num_cols = [
      'Temperature',
      'Humidity',
      'SquareFootage',
      'Occupancy',
      'RenewableEnergy',
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

  for col in [
      'Temperature',
      'Humidity',
      'SquareFootage',
      'Occupancy',
      'RenewableEnergy',
      'EnergyConsumption',
  ]:
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
      data=df[['Temperature', 'Humidity', 'Occupancy', 'RenewableEnergy']],
      ax=ax,
      palette='Set2',
  )
  st.pyplot(fig)

  st.markdown('---')

  # =====================================================================
  # 3단계: 이상치 정제(클리핑) 및 파일 다운로드
  # =====================================================================
  st.header('3단계: 이상치 정제(클리핑) 및 정제 파일 생성')
  df_processed = df.copy()
  for col in [
      'Temperature',
      'Humidity',
      'SquareFootage',
      'Occupancy',
      'RenewableEnergy',
      'EnergyConsumption',
  ]:
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
  # 4단계: 9개 독립변수 전수 EDA 시각화 (핵심!)
  # =====================================================================
  st.header('4단계: 독립변수 9개 전체에 대한 탐색적 분석(EDA) 및 시각화')
  st.write(
      '모델에 투입할 **수치형 독립변수 5개**와 **범주형 독립변수 4개**가 타겟('
      'EnergyConsumption)과 각각 어떤 관계를 가지는지 빠짐없이 검증합니다.'
  )

  # --- [A] 수치형 독립변수 5개 시각화 (산점도 + 추세선) ---
  st.subheader('📈 [수치형 독립변수 5개] vs 에너지 소비량 산점도')
  numeric_features = [
      'Temperature',
      'Humidity',
      'SquareFootage',
      'Occupancy',
      'RenewableEnergy',
  ]

  # 2개씩 컬럼 나누어 깔끔하게 배치
  for i in range(0, len(numeric_features), 2):
    c1, c2 = st.columns(2)

    with c1:
      feat1 = numeric_features[i]
      st.write(f'**{feat1} vs EnergyConsumption**')
      fig, ax = plt.subplots(figsize=(6, 4))
      sns.scatterplot(
          data=df_processed,
          x=feat1,
          y='EnergyConsumption',
          ax=ax,
          alpha=0.6,
          color='royalblue',
      )
      sns.regplot(
          data=df_processed,
          x=feat1,
          y='EnergyConsumption',
          scatter=False,
          ax=ax,
          color='red',
      )
      st.pyplot(fig)

    with c2:
      if i + 1 < len(numeric_features):
        feat2 = numeric_features[i + 1]
        st.write(f'**{feat2} vs EnergyConsumption**')
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(
            data=df_processed,
            x=feat2,
            y='EnergyConsumption',
            ax=ax,
            alpha=0.6,
            color='seagreen',
        )
        sns.regplot(
            data=df_processed,
            x=feat2,
            y='EnergyConsumption',
            scatter=False,
            ax=ax,
            color='red',
        )
        st.pyplot(fig)

  st.markdown('---')

  # --- [B] 범주형 독립변수 4개 시각화 (막대그래프) ---
  st.subheader('📊 [범주형 독립변수 4개]별 평균 에너지 소비량 (막대그래프)')
  cat_features = ['HVACUsage', 'LightingUsage', 'DayOfWeek', 'Holiday']

  for i in range(0, len(cat_features), 2):
    c3, c4 = st.columns(2)

    with c3:
      cat1 = cat_features[i]
      st.write(f'**{cat1}에 따른 평균 에너지 소비량**')
      fig, ax = plt.subplots(figsize=(6, 4))
      cat_mean = (
          df_processed.groupby(cat1)['EnergyConsumption']
          .mean()
          .reset_index()
      )
      sns.barplot(
          data=cat_mean, x=cat1, y='EnergyConsumption', palette='Set2', ax=ax
      )
      st.pyplot(fig)

    with c4:
      if i + 1 < len(cat_features):
        cat2 = cat_features[i + 1]
        st.write(f'**{cat2}에 따른 평균 에너지 소비량**')
        fig, ax = plt.subplots(figsize=(6, 4))
        cat_mean2 = (
            df_processed.groupby(cat2)['EnergyConsumption']
            .mean()
            .reset_index()
        )
        sns.barplot(
            data=cat_mean2,
            x=cat2,
            y='EnergyConsumption',
            palette='Pastel1',
            ax=ax,
        )
        st.pyplot(fig)

  # --- [C] 수치형 변수 전체 상관관계 히트맵 ---
  st.subheader('🔥 [종합] 수치형 변수 전체 상관관계 히트맵')
  fig, ax = plt.subplots(figsize=(8, 5))
  sns.heatmap(
      df_processed[
          [
              'Temperature',
              'Humidity',
              'SquareFootage',
              'Occupancy',
              'RenewableEnergy',
              'EnergyConsumption',
          ]
      ].corr(),
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
