import streamlit as st
from plotting_streamlit import data_import, format_for_streamlit, settings, add_bg_from_local, today_times, user_multi_select_all_users, mum_selector

# Imports default settings
settings()

# Imports data
collection_list = ['Times']
mum_selector(collection_list)
df = data_import(collection_list)
df = format_for_streamlit(df)

# Sets background
add_bg_from_local()

df, fig = today_times(df)

# Selects users to display
df = user_multi_select_all_users(df)

# Display plot
st.pyplot(fig)

# Displays dataframe
df.columns = df.columns.str.capitalize()
st.dataframe(df.set_index('User'), width=800)