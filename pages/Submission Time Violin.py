import streamlit as st
from plotting_streamlit import data_import, data_cleaning_and_prep, settings, sub_time_violin_plot, add_bg_from_local
# Gets default settings
palette, figsize, user, window_days = settings()
# Imports data
df = data_import()

df = data_cleaning_and_prep(df)
# Gets plot
fig = sub_time_violin_plot(df, palette)

# Sets background
add_bg_from_local()

st.set_page_config(layout='wide')
# Sets title
st.title('Submission Time Dist Plot')
# Display plot
st.pyplot(fig)

add_bg_from_local()

