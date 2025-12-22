import streamlit as st
from plotting_streamlit import welcome_gif, data_import, format_for_streamlit, add_bg_from_local, user_multi_select_non_mums, date_select, mum_selector, retro_selector

# Loads gif
welcome_gif()

# Sets background
add_bg_from_local()

# Imports data
collection_list = ['Times']
mum_selector(collection_list)

df = data_import(collection_list)
df = format_for_streamlit(df)

# Sets background
add_bg_from_local()

# Selects users to display
df = user_multi_select_non_mums(df)

df = retro_selector(df)

# Selects date range
df = date_select(df)

# Displays dataframe
df.columns = df.columns.str.capitalize()
df.index.name = df.index.name.capitalize()
st.dataframe(df[['Time', 'User']], width=800)

# Writes number of rows in database
st.write(str(df.shape[0]) + ' rows found')
