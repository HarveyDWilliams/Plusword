import streamlit as st
from plotting_streamlit import data_import, settings, overall_times, add_bg_from_local, format_for_streamlit, user_multi_select_non_mums, mum_selector, retro_selector

# Imports default settings
settings()

# Imports data
collection_list = ['Times']
mum_selector(collection_list)
df = data_import(collection_list)
df = format_for_streamlit(df)

df = retro_selector(df)

# Sets background
add_bg_from_local()

# Selects chart type
chart_type = st.sidebar.radio(label='Select chart type',
                              options=["Mean", 'Quickest', 'Slowest'])

# Selects users to display
df = user_multi_select_non_mums(df)

if chart_type == 'Mean':
    agg = 'Mean'
    df, fig = overall_times(df, agg)

elif chart_type == 'Quickest':
    agg = 'Min'
    df, fig = overall_times(df, agg)

else:
    agg = 'Max'
    df, fig = overall_times(df, agg)

# Display plot
st.pyplot(fig)

# Displays dataframe
df.columns = df.columns.str.capitalize()
st.dataframe(df.set_index('User'), width=800)
