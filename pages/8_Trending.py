import streamlit as st
from plotting_streamlit import data_import, palette_import, include_mums, settings, user_multi_select, date_select,\
    combined_period_mean, rolling_average, add_bg_from_local

# Gets default settings
settings()

# Imports data
df = data_import()
palette = palette_import()
df = include_mums(df)

# Selects users to display
df = user_multi_select(df)

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

    df, fig = combined_period_mean(df, palette, time_period, smooth, poly_value)

# Selects weekly mean times
elif chart_type == 'Weekly Mean':

    # Sets value for amount of smoothing
    if smooth:
        poly_value = st.sidebar.slider('Smoothies',
                                       min_value=1,
                                       max_value=10,
                                       value=10,
                                       help='Higher values give smoother lines, lower values give rougher lines')

    # Default value if smoothing isn't selected
    else:
        poly_value = 0

    # 'W' = week
    time_period = 'W'

    df, fig = combined_period_mean(df, palette, time_period, smooth, poly_value)

# Selects rolling average
else:
    window_days = st.sidebar.slider('Window Days',
                                    min_value=1,
                                    max_value=150,
                                    value=60,
                                    help='Number of days over which to average times')

    df, fig = rolling_average(df, palette, window_days)
    chart_type = str(window_days) + ' Day ' + chart_type

# Sets title
st.title(chart_type)

# Display plot
st.pyplot(fig)

# Displays dataframe
st.dataframe(df.set_index('User'), width=800)
