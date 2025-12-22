import streamlit as st
from plotting_streamlit import data_import, settings, puzzle_difficulty, add_bg_from_local, format_for_streamlit

# Imports default settings
settings()


# Imports data
collection_list = ['Times']
df = data_import(collection_list)
df = format_for_streamlit(df)

# Sets background
add_bg_from_local()

# Selects chart type
difficulty = st.sidebar.radio(label='Select difficulty',
                              options=["Easiest", 'Hardest'])

# Selects number of rows to return
number_of_rows = st.sidebar.slider('Select number of rows',
                                   min_value=1,
                                   max_value=100,
                                   value=20)
# Selects difficulty
if difficulty == 'Easiest':
    ascending = True
    df, fig = puzzle_difficulty(df, ascending, number_of_rows)

else:
    ascending = False
    df, fig = puzzle_difficulty(df, ascending, number_of_rows)

# Display plot
st.pyplot(fig)

# Displays dataframe
df.columns = df.columns.str.capitalize()
st.dataframe(df, width=800)
