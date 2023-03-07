import streamlit as st
from plotting_streamlit import data_import, data_cleaning_and_prep, settings, overall_mean_time

palette, figsize, user, window_days = settings()

df = data_import()

df = data_cleaning_and_prep(df)

df_overall_mean_time, fig = overall_mean_time(df, palette)

st.title('Mean Times')

st.pyplot(fig)

st.dataframe(df_overall_mean_time.set_index('User'), width=800)