import streamlit as st
from plotting_streamlit import data_import, palette_import, add_bg_from_local, user_multi_select, date_select, \
    include_mums

# Imports data
df = data_import()
palette = palette_import()
df = include_mums(df)

# Selects users to display
df = user_multi_select(df)

# Selects date range
df = date_select(df)

# Formats dataframe
df.columns = df.columns.str.capitalize()
df = df.set_index('Timestamp')
df = df.sort_index(ascending=False)

# Sets background
add_bg_from_local()

# Sets title
st.title('Data display')

# Displays dataframe
st.dataframe(df[['Time', 'User']], width=800)

# Writes number of rows in database
st.write(str(df.shape[0]) + ' rows found')
