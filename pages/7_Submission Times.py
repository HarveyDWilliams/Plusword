import streamlit as st
from plotting_streamlit import data_import, format_for_streamlit, settings, add_bg_from_local,\
    user_single_select, sub_time_violin_plot, sub_time_distplot, sub_time_boxplot, user_multi_select_non_mums, mum_selector

# Imports default settings
settings()


# Imports data
collection_list = ['Times']
mum_selector(collection_list)
df = data_import(collection_list)
df = format_for_streamlit(df)

# Sets background
add_bg_from_local()

# Selects chart type
chart_type = st.sidebar.radio(label='Select chart type',
                              options=["Violin Plot", 'Dist Plot', 'Box Plot'])

# # Selects users to display
# df = user_multi_select_non_mums(df)

if chart_type == 'Violin Plot':

    # Selects users to display
    df = user_multi_select_non_mums(df)
    fig = sub_time_violin_plot(df)

elif chart_type == 'Dist Plot':

    # Selects users
    df, user = user_single_select(df)
    fig = sub_time_distplot(df, user)

else:
    # Selects users to display
    df = user_multi_select_non_mums(df)
    fig = sub_time_boxplot(df)

# Display plot
st.pyplot(fig)
