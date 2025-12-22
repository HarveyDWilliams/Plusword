import streamlit as st
from plotting_streamlit import data_import, settings, user_multi_select_non_mums, date_select,\
    combined_period_mean, rolling_average, add_bg_from_local, format_for_streamlit, mum_selector, retro_selector

# Imports default settings
settings()

# Imports data
collection_list = ['Times']
mum_selector(collection_list)
df = data_import(collection_list)
df = format_for_streamlit(df)
df = retro_selector(df)

# Selects date range
df = date_select(df)

# Sets background
add_bg_from_local()

# Selects chart type
chart_type = st.sidebar.radio(label='Select chart type',
                              options=["Monthly Mean", 'Weekly Mean', 'Rolling Average'])

# Hides smoothing option if rolling average selected
if chart_type != 'Rolling Average':
    smooth = st.sidebar.checkbox('Smooth Data')

df = user_multi_select_non_mums(df)

# Selects monthly mean times
if chart_type == 'Monthly Mean':

    # Sets value for amount of smoothing
    if smooth:
        poly_value = st.sidebar.slider('Smoothies',
                                       min_value=0,
                                       max_value=40,
                                       value=40,
                                       help='Higher values give smoother lines, lower values give rougher lines')

    # Default value if smoothing not selected
    else:
        poly_value = 6

    # M = month
    time_period = 'M'

    df, fig = combined_period_mean(df, time_period, smooth, poly_value)

# Selects weekly mean times
elif chart_type == 'Weekly Mean':

    # Sets value for amount of smoothing
    if smooth:
        poly_value = st.sidebar.slider('Smoothies',
                                       min_value=1,
                                       max_value=10,
                                       value=5,
                                       help='Higher values give smoother lines, lower values give rougher lines')

    # Default value if smoothing isn't selected
    else:
        poly_value = 0

    # 'W' = week
    time_period = 'W'

    df, fig = combined_period_mean(df, time_period, smooth, poly_value)

# Selects rolling average
else:
    window_days = st.sidebar.slider('Window Days',
                                    min_value=1,
                                    max_value=150,
                                    value=60,
                                    help='Number of days over which to average times')

    df, fig = rolling_average(df, window_days)
    chart_type = str(window_days) + ' Day ' + chart_type

# Display plot
st.pyplot(fig)

# Displays dataframe
st.dataframe(df.set_index('user'), width=800)
