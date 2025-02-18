import base64
from datetime import datetime, timedelta, date
import json
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymongo
import seaborn as sns
import streamlit as st
import random
from scipy import interpolate, signal


## TODO: Add streak
## TODO: Add sub minute/submissions ratio
## TODO: Add outline to mums


def settings():
    # Sets plot style

    sns.set_theme()


def time_delta_to_num(time_delta):
    """ Takes in time delta and converts it into a number for plotting"""

    # specify a date to use for the times

    zero_date = datetime(2022, 6, 20)

    zero_num = mdates.date2num(zero_date)

    # adds zero_data to timedelta to convert

    time_delta_plus_date = [zero_date + time_unit for time_unit in time_delta]

    # convert datetimes to numbers

    time_delta_as_num = [mins - zero_num for mins in mdates.date2num(time_delta_plus_date)]

    return time_delta_as_num


def time_string_to_time_delta(time_string):
    """ Reads in times from the database and corrects incorrect values"""
    try:
        # If count is one then we have 00:00 format
        if time_string.count(":") == 1:
            if len(time_string) != 5:
                # We could do something clever to fix this but let's just assume the data is invalid and skip it
                return None
            time_string = f"00:{time_string}"
        # If length is two then we have at least a 0:00:00 format, which is valid
        if time_string.count(":") == 2:
            return pd.to_timedelta(time_string)
        else:
            # Another invalid string, just skip it.
            return None

    except Exception as ex:
        # Obviously the above is not perfect, so we wanna account for exceptions
        # We don't have logging in the code, which we should, so I'm just throwing it in the terminal
        # Unfortunately pandas throws a base exception so this could
        # catch all sorts so best we can do is dump to terminal and return None
        print(ex)
        return None


def time_delta_as_num_to_time(df):
    """Creates a human-readable time from a timedelta and strips the UNIX date from the value to just leave the time"""

    df['Time'] = mdates.num2date(df['time_delta_as_num'])

    df['Time'] = df['Time'].dt.time

    df['Time'] = df['Time'].astype('string')

    df['Time'] = df['Time'].str[:8]

    return df


def y_axis_generator(max_y_value, unit):
    """Creates range for y axis from 0 to max_y_value then passes it to time_delta_to_num. Returns y axis values as
    plottable number"""

    y_axis_time_range = list(range(0, max_y_value, 1))

    y_axis_time_delta = pd.to_timedelta(y_axis_time_range, unit=unit)

    y_axis_time_num = time_delta_to_num(y_axis_time_delta)

    return y_axis_time_num


def spline_smooth(df, poly_value):
    """Smooths lines via interpolation and splines. Purely cosmetic"""

    df_spline = df.copy()

    df_spline['date_as_num'] = mdates.date2num(df_spline['timestamp'])

    x_smooth = np.linspace(df_spline['date_as_num'].min(), df_spline['date_as_num'].max(), poly_value)

    bspline = interpolate.make_interp_spline(df_spline['date_as_num'], df_spline['time_delta_as_num'])

    y_smooth = bspline(x_smooth)

    return x_smooth, y_smooth


def savgol_smooth(df, poly_value):
    """Smooths lines using a Savitzky–Golay filter"""

    df_savgol = df.copy()

    df_savgol['date_as_num'] = mdates.date2num(df_savgol['timestamp'])

    max_window = len(df_savgol)

    x_smooth = signal.savgol_filter(df_savgol['date_as_num'], max_window, poly_value)

    y_smooth = signal.savgol_filter(df_savgol['time_delta_as_num'], max_window, poly_value)

    return x_smooth, y_smooth


def get_db(write=False):
    if write:
        connection_string = "admin_connection_string"

    else:
        connection_string = "connection_string"

    try:
        with open("local/pass.json") as file:
            file = json.loads(file.read())
            connection_string = file.get(connection_string)
            client = pymongo.MongoClient(
                connection_string)
            db = client["PlusWord"]
            return db
    except Exception as e:
        print(e)


def palette_import():
    ##TODO: remove
    # Gets colours from db
    db = get_db()
    collection = db["Colours"]
    df_palette = pd.DataFrame(list(collection.find({})))
    df_palette = df_palette[['user', 'colour']]
    palette = dict(zip(df_palette['user'], df_palette['colour']))

    return palette


# def data_import(collection_name='Times'):
#     """Connects to database and creates dataframe containing all columns. Drops unneeded columns and sets timestamp
#      datatype. Correct any incorrect time values, sets data times and sorts"""
#
#     # Connects to db and gets collection
#     db = get_db()
#     collection = db[collection_name]
#     df = pd.DataFrame(list(collection.find({})))
#
#     return df

def data_import(include_mums=False):
    """Connects to database and creates dataframe containing all columns. Drops unneeded columns and sets timestamp
     datatype. Correct any incorrect time values, sets data times and sorts"""

    collection_list = ['Times']

    if include_mums:
        collection_list.append('Mumsnet_Times')
    all_records = []

    # Connects to db and gets collection
    db = get_db()

    for collection in collection_list:
        records = list(db[collection].find())
        all_records.append(records)

    # Flattens list
    all_records = [val for sublist in all_records for val in sublist]

    df = pd.DataFrame(all_records)

    # Makes column to indicate which database times are from
    non_mums = ['Harvey Williams', 'Sazzle', 'Leah', 'Tom', 'Joe', 'George Sheen', 'Oliver Folkard']
    df['mum'] = np.where(df['user'].isin(non_mums), False, True)

    return df


def format_for_streamlit(df):
    """Makes df more readable, converts times into plottable numbers and sets index"""

    df = df[['load_ts', 'time', 'user']]
    df['time'] = df['time'].str.replace(r'(^\d\d:\d\d$)', r'00:\1', regex=True)
    df['load_ts'] = pd.to_datetime(df['load_ts'], format='%Y-%m-%d %H:%M:%S.%f')
    df['user'] = df['user'].str.split(' ', 1).str[0]
    df = df.sort_values(by=['load_ts'])
    df = df.rename(columns={'load_ts': 'timestamp'})
    df['time_delta'] = pd.to_timedelta(df['time'].astype('timedelta64[ns]'))
    df['time_delta_as_num'] = time_delta_to_num(pd.to_timedelta(df['time'].astype('string')))
    df['sub_time_delta_as_num'] = time_delta_to_num(pd.to_timedelta(df['timestamp'].dt.time.astype('string')))

    df = df.set_index('timestamp')
    df = df.sort_index(ascending=False)

    return df


def old_data_import(collection_name='Times'):
    """Connects to database and creates dataframe containing all columns. Drops unneeded columns and sets timestamp
     datatype. Creates submission time from timestamp and converts both submission time and completion time to time
     deltas represented as plottable numbers. Finally, drops submission time column as no longer needed"""

    # Connects to db and gets collection
    db = get_db()
    collection = db[collection_name]
    df = pd.DataFrame(list(collection.find({})))
    df = df[['load_ts', 'time', 'user']]
    # df['load_ts'] = pd.to_datetime(df['load_ts'], format='%Y-%m-%d %H:%M:%S.%f%z')
    df = df.sort_values(by=['load_ts'], ascending=False)
    df = df.rename(columns={'load_ts': 'timestamp'})

    # Dropping columns and setting datatypes

    # Instead of rewriting the code I've just reassigned my load_ts to your timestamp
    # I have removed the timezone for legibility
    df["timestamp"] = pd.to_datetime(df["load_ts"], format='%Y-%m-%d %H:%M:%S.%f%z')
    df["timestamp"] = df["timestamp"].dt.tz_localize(None)
    #
    # Dropping columns and setting datatypes
    df = df[['timestamp', 'time', 'user']]
    #
    # Converting time and submission time to timedelta
    # this throws a warning regarding overwriting data, @Tom pls fix
    # I've just suppressed the warning as the operation is correct
    df["time_delta"] = df["time"].astype('string')
    df["time_delta"] = df["time_delta"].map(time_string_to_time_delta)
    df['time'] = df['time'].str.replace(r'(^\d\d:\d\d$)', r'00:\1', regex=True)
    df['time_delta'] = df['time'].astype('timedelta64[ns]')

    df['sub_time_delta'] = df['timestamp'].dt.strftime('%H:%M:%S').astype('timedelta64')

    # Converting timedeltas to plottable numbers and dropping sub_time_delta

    for col in ['time_delta', 'sub_time_delta']:
        df['new'] = df[col].astype('timedelta64[ns]')
        df['new'] = time_delta_to_num(df['new'])
        df.rename(columns={'new': str(col) + '_as_num'}, inplace=True)

    df = df.drop(columns="sub_time_delta")
    df = df.rename(columns={'user': 'User'})

    return df


def overall_times(df, palette, agg):
    """Barplot showing the longest completion time for each person """

    ## TODO: Bring date through with max and min
    ## TODO: Make default number of mums come through

    more_than_3_entries = df['user'].value_counts() > 3

    if agg == 'Mean':
        df = df.groupby(df["user"])["time_delta_as_num"].mean()

    if agg == 'Min':
        df = df.groupby(df["user"])["time_delta_as_num"].min()

    if agg == 'Max':
        df = df.groupby(df["user"])["time_delta_as_num"].max()

    df = df[more_than_3_entries]

    df = df.reset_index()

    df = df.sort_values(by='time_delta_as_num', ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))

    fig = sns.barplot(data=df,
                      x="user",
                      y="time_delta_as_num",
                      ).set(
        ylabel='Time /mins',
        xlabel=None)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    df = time_delta_as_num_to_time(df)

    df = df[['user', 'Time']]

    return df, ax.figure


def number_of_sub_1_minnies(df, palette):
    """ Barplot of how many sub 1-minute completion times for each person"""

    # Creates df

    df_sub_minnies = df[df["time_delta"] < timedelta(minutes=1)]

    df_sub_minnies = df_sub_minnies.reset_index()

    df_sub_minnies = df_sub_minnies.groupby(df_sub_minnies["user"])["timestamp"].count()

    df_sub_minnies = df_sub_minnies.reset_index()

    df_sub_minnies = df_sub_minnies.rename(columns={'timestamp': 'Number of Sub 1 Minutes'})

    df_sub_minnies = df_sub_minnies.sort_values(by='Number of Sub 1 Minutes', ascending=False)

    # Plot

    fig, ax = plt.subplots(figsize=(10, 5))

    fig = sns.barplot(data=df_sub_minnies,
                      y='Number of Sub 1 Minutes',
                      x='user'
                      ).set(
        ylabel=None,
        xlabel=None)

    plt.xticks(rotation=0)

    return df_sub_minnies, ax.figure


def number_of_submissions(df, palette):
    """ Barplot of how many submissions total for each person"""

    # Creates df

    df_overall_number_submissions = df["user"].value_counts(sort=True, ascending=False)

    df_overall_number_submissions = df_overall_number_submissions.reset_index()

    df_overall_number_submissions = df_overall_number_submissions.rename(columns={'user': 'Number of Submissions',
                                                                                  'index': 'User'})
    # Plot

    fig, ax = plt.subplots(figsize=(10, 5))

    fig = sns.barplot(data=df_overall_number_submissions,
                      y='Number of Submissions',
                      x='User'
                      ).set(
        ylabel=None,
        xlabel=None)

    plt.xticks(rotation=0)

    return df_overall_number_submissions, ax.figure


def combined_period_mean(df, palette, time_period, smooth, poly_value):
    """Plots mean times for every player over time on the same lineplot"""

    # Creates df

    df_mean_time = df.groupby(["User", df["timestamp"].datetime.to_period(time_period)])["time_delta_as_num"].mean()

    df_mean_time = df_mean_time.reset_index()

    # Generates 25 mins for y-axis

    y_axis_time = y_axis_generator(25, 'm')

    # Displays every 2 mins

    y_axis_time_num_2_mins = y_axis_time[::2]

    fig, ax = plt.subplots(figsize=(15, 7))

    # Smooths lines out for each user and plots them

    if smooth:

        df_smooth = pd.DataFrame()

        for User in df_mean_time['User'].unique():

            df_mean_time_rough = df_mean_time[df_mean_time['User'] == User]

            try:
                if time_period == 'M':
                    x_smooth, y_smooth = spline_smooth(df_mean_time_rough, poly_value)

                if time_period == 'W':
                    x_smooth, y_smooth = savgol_smooth(df_mean_time_rough, poly_value)

            except Exception:

                # If smoothing function errors just plot original values
                x_smooth = mdates.date2num(df_mean_time_rough['timestamp']).tolist()

                y_smooth = df_mean_time_rough['time_delta_as_num'].tolist()

            # converts x_smooth, y_smooth into a dataframe with user value associated with them

            user_list = [User] * len(x_smooth)

            x_smooth = pd.Series(x_smooth, name='date_as_num')

            y_smooth = pd.Series(y_smooth, name='time_delta_as_num')

            users = pd.Series(user_list, name='User')

            df = pd.concat([users, x_smooth, y_smooth], axis=1)

            # Concats dfs together to make one big one

            df_smooth = pd.concat([df_smooth, df])

        df = df_smooth.copy()

    else:
        df = df_mean_time.copy()

        df['date_as_num'] = mdates.date2num(df['timestamp'])

    # Plotting

    fig = sns.lineplot(data=df,
                       x='date_as_num',
                       y='time_delta_as_num',
                       hue='User'
                       ).set(
        xlabel='Date',
        ylabel='Mean time /min')

    ax.yaxis_date()

    ax.set_yticks(y_axis_time_num_2_mins)

    ax.set_yticklabels(y_axis_time_num_2_mins)

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    # Formats df

    df_mean_time = time_delta_as_num_to_time(df_mean_time)

    df_mean_time['Date'] = df_mean_time['timestamp'].datetime.strftime('%d %B %Y')

    df_mean_time = df_mean_time[['User', 'Date', 'Time']]

    df_mean_time = df_mean_time.rename(columns={'Time': 'Mean Time'})

    return df_mean_time, ax.figure


def rolling_average(df, palette, window_days):
    """ Finds rolling average over window_days number of days for each user. Then joins all dataframes together"""

    window_days_str = str(window_days) + 'd'

    df_ra_list = []

    for user in df["User"].unique():
        df_ra = df[df["User"] == user]

        df_ra = df_ra.sort_values(by='timestamp')

        df_ra = df_ra.set_index("timestamp")

        df_ra["time_delta_as_num"] = df_ra["time_delta_as_num"].rolling(window=window_days_str).mean()

        df_ra["time_delta"] = mdates.num2timedelta(df_ra["time_delta_as_num"])

        df_ra = df_ra[['User', 'time_delta', "time_delta_as_num"]]

        df_ra_list.append(df_ra)

        df_ra_finished = pd.concat(df_ra_list)

    df_ra_finished = df_ra_finished.reset_index()

    fig, ax = plt.subplots(figsize=(15, 7))

    fig = sns.lineplot(data=df_ra_finished,
                       x='timestamp',
                       y='time_delta_as_num',
                       hue='User',
                       ).set(
        xlabel='Date',
        ylabel='Rolling Mean Times /min')

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    ax.set_ylim(ymin=0)

    df_ra_finished = time_delta_as_num_to_time(df_ra_finished)

    df_ra_finished['Date'] = df_ra_finished['timestamp'].datetime.strftime('%d %B %Y')

    df_ra_finished = df_ra_finished[['User', 'Date', 'Time']]

    df_ra_finished = df_ra_finished.rename(columns={'Time': 'Mean Time'})

    return df_ra_finished, ax.figure


def sub_time_boxplot(df, palette):
    """Plots boxplot of submission times"""

    ## TODO: Remove users with less than three entries
    ## TODO: Make default number of mums come through

    fig, ax = plt.subplots(figsize=(15, 7))

    fig = sns.boxplot(data=df,
                      x="user",
                      y="sub_time_delta_as_num",
                      ).set(
        ylabel='Time of Submission',
        xlabel=None)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    ax.set_ylim(ymin=0)

    return ax.figure


def sub_time_violin_plot(df, palette):
    """Plots violin plot of submission times"""

    ## TODO: Remove users with less than three entries
    ## TODO: Make default number of mums come through

    # Generates 24 hours for y axis

    y_axis_time = y_axis_generator(24, 'h')

    # selects every 2 hours

    y_axis_time_2_hourly = y_axis_time[::2]

    fig, ax = plt.subplots(figsize=(15, 7))

    fig = sns.violinplot(data=df,
                         x="user",
                         y=df["sub_time_delta_as_num"],
                         cut=0,
                         bw=0.25)

    ax.yaxis_date()

    ax.set_yticks(y_axis_time_2_hourly)

    ax.set_yticklabels(y_axis_time_2_hourly)

    ax.set_xlabel(None)

    ax.set_ylabel('Time of Submission')

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    ax.set_ylim(ymin=0)

    return ax.figure


def sub_time_distplot(df, palette, user):
    """Plots dist plot for submission times based on user"""

    # more_than_3_entries = df['user'].value_counts() > 3
    ## TODO: Remove users with less than three entries

    df_time_dist = df.sort_values(by='sub_time_delta_as_num')

    df_time_dist = df[more_than_3_entries]

    fig, ax = plt.subplots(figsize=(15, 7))
    palette = sns.color_palette("hls", 20)

    plt.xlim(0, 1)

    fig = sns.distplot(df_time_dist,
                       x=df_time_dist['sub_time_delta_as_num'],
                       bins=30,
                       kde=True,
                       color=palette[random.randint(0, 20)]).set(
        title=user,
        xlabel='Time of Submission')

    ax.xaxis_date()

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    return ax.figure


def puzzle_difficulty(df, ascending, number_of_rows):
    """Returns df and scatterplot of highest or lowest mean times across all users"""

    ## TODO: Change Hue based on mum
    ## TODO: Add tool tip

    # Creates df

    df_difficulty = df.copy()

    df_difficulty['date'] = df_difficulty.index.date

    more_than_3_entries = df_difficulty['date'].value_counts() > 3

    df_difficulty = df_difficulty.groupby(['date'])['time_delta_as_num'].mean()

    # df_difficulty[more_than_3_entries]

    df_difficulty = df_difficulty.reset_index()

    df_difficulty = df_difficulty.sort_values(by='time_delta_as_num', ascending=ascending)

    # Selects 20 hardest

    df_difficulty = df_difficulty[:number_of_rows]

    df_difficulty['time'] = mdates.num2timedelta(df_difficulty['time_delta_as_num'])

    fig, ax = plt.subplots(figsize=(10, 5))

    fig = sns.scatterplot(data=df_difficulty,
                          x='date',
                          y='time_delta_as_num',
                          hue='mum')

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    ax.set_xlabel(None)

    ax.set_ylabel('Mean Time /mins')

    ax.set_ylim(ymin=0)

    # Formats df

    df_difficulty = time_delta_as_num_to_time(df_difficulty)

    df_difficulty = df_difficulty[['date', 'Time']]
    df_difficulty = df_difficulty.set_index('date')

    return df_difficulty, ax.figure


def add_bg_from_local():
    """Creates background for streamlit from image"""

    image_file = 'media/plusword_background.jpg'

    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
        unsafe_allow_html=True
    )


def welcome_gif():
    """Displays welcome gif"""

    file_ = open(r'media/completion-animation.gif', 'rb')
    contents = file_.read()
    data_url = base64.b64encode(contents).decode('utf-8')
    file_.close()

    st.markdown(
        f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
        unsafe_allow_html=True,
    )


def user_multi_select(df):
    """Creates multiselect box containing unique users names. Filters df to only contain those users"""

    sorted_unique_user = sorted(df['user'].unique())

    selected_users = st.sidebar.multiselect('User', sorted_unique_user, sorted_unique_user)

    df = df[df['user'].isin(selected_users)]

    return df


def user_single_select(df):
    """Creates select box containing unique users names. Filters df to only contain that user"""

    sorted_unique_user = df['user'].unique()

    selected_user = st.sidebar.selectbox('User', sorted_unique_user)

    df = df[df['user'] == selected_user]

    return df, selected_user


def date_select(df):
    """Creates date picker and returns df filtered to be between those dates"""

    start_date = st.sidebar.date_input('Start date', df.index.date.min())

    end_date = st.sidebar.date_input('End date', datetime.today())

    df['date'] = df.index.date

    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    return df


def mum_selector(include_mums=False):
    """ Allows selection of mumsnet data"""

    include_mums = st.sidebar.checkbox('Include Mums?', value=False)

    return include_mums


def today_times(df, include_mums):
    df_today = df.loc[(df.index.date == date.today())]
    df_today = df_today.reset_index()
    df_today = df_today.sort_values(by='time_delta_as_num', ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))

    fig = sns.barplot(data=df_today,
                      y='time_delta_as_num',
                      x='user',
                      ).set(
        ylabel='Time /mins',
        xlabel=None)

    if include_mums:
        plt.xticks(rotation=90)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    df_today = time_delta_as_num_to_time(df_today)

    df_today = df_today[['user', 'time']]

    return df_today, ax.figure
