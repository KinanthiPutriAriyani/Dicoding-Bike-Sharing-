import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import altair as alt
import numpy as np

# Load data
all_df = pd.read_csv("dashboard/all_df.csv")
all_df['dateday'] = pd.to_datetime(all_df['dateday'])

st.set_page_config(page_title="Bike-sharing Dashboard",
                   page_icon="🚴‍♂️",
                   layout="wide")


def create_monthly_users_df(all_df):
    monthly_users_df = all_df.set_index('dateday').resample(rule='M').agg({
        "unregistered_x": "sum",
        "registered_x": "sum",
        "count_x": "sum"
    })
    monthly_users_df.index = monthly_users_df.index.strftime('%b-%y')
    monthly_users_df = monthly_users_df.reset_index()
    monthly_users_df.rename(columns={
        "dateday": "yearmonth",
        "count_x": "count",
        "unregistered_x": "unregistered",
        "registered_x": "registered"
    }, inplace=True)
    
    return monthly_users_df

# Helper function to calculate average bike rentals per hour on weekdays and weekends
def calculate_hourly_average(all_df):
    all_df['weekday'] = all_df['dateday'].dt.weekday
    hourly_average = all_df.groupby(['weekday', 'hour'])['count_x'].mean().reset_index()
    return hourly_average

def create_seasonly_users_df(all_df):
    yearly_data = all_df[all_df['year_x'] == 'year_x']
    seasonly_users_df = yearly_data.groupby("season_x").agg({
        "unregistered_x": "sum",
        "registered_x": "sum",
        "count_x": "sum"
    })
    seasonly_users_df = seasonly_users_df.reset_index()
    seasonly_users_df.rename(columns={
        "count_x": "count",
        "unregistered_x": "unregistered",
        "registered_x": "registered"
    }, inplace=True)
    
    seasonly_users_df = pd.melt(seasonly_users_df,
                                id_vars=['season_x'],
                                value_vars=['unregistered', 'registered'],
                                var_name='type_of_rides',
                                value_name='count_rides')
    
    seasonly_users_df['season'] = pd.Categorical(seasonly_users_df['season_x'],
                                                 categories=['spring', 'summer', 'fall', 'winter'])
    
    seasonly_users_df = seasonly_users_df.sort_values('season')
    
    return seasonly_users_df

# Helper function to calculate average bike rentals per day over the months for the years 2011 and 2012
def calculate_monthly_average(all_df):
    all_df['year'] = all_df['dateday'].dt.year
    monthly_average = all_df.groupby(['year_y', 'month_y'])['count_y'].mean().reset_index()
    return monthly_average

# make filter components (komponen filter)

min_date = all_df["dateday"].min()
max_date = all_df["dateday"].max()

# ----- SIDEBAR -----
with st.sidebar:
    # add logo
    st.image("assets/sepeda.png")

    st.markdown("<h1 style='text-align: center;'>Date Filter</h1>", unsafe_allow_html=True)

    # mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Select Date Range:",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

st.sidebar.markdown("<h1 style='text-align: center; font-size:20px;'>Les't Connet With Me</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.sidebar.columns([1,1,1])

with col1:
    st.markdown("[![LinkedIn](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/in/kinanthi-putri/)")
with col2:
    st.markdown("[![Instagram](https://skillicons.dev/icons?i=instagram)](https://www.instagram.com/kinanthipa/)")
with col3:
    st.markdown("[![Github](https://skillicons.dev/icons?i=github)](https://github.com/KinanthiPutriAriyani)")

# hubungkan filter dengan main_df
main_df = all_df[
    (all_df["dateday"] >= str(start_date)) &
    (all_df["dateday"] <= str(end_date))
]

# assign main_df ke helper functions yang telah dibuat sebelumnya

monthly_users_df = create_monthly_users_df(main_df)
hourly_average_df = calculate_hourly_average(main_df)
seasonly_users_df = create_seasonly_users_df(main_df)
monthly_average_df = calculate_monthly_average(main_df)

# ----- MAINPAGE -----
st.title(":chart_with_upwards_trend: Bike Sharing Analytics")
st.markdown("##")

col1, col2, col3 = st.columns(3)

with col1:
    total_all_rides = main_df['count_x'].sum()
    st.metric("Total user", value=total_all_rides)
with col2:
    total_unregistered = main_df['unregistered_x'].sum()
    st.metric("Total unregistered User", value=total_unregistered)
with col3:
    total_registered = main_df['registered_x'].sum()
    st.metric("Total registered User", value=total_registered)

st.markdown("---")

# ----- CHART -----

# Tren pengguna sepeda
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=monthly_users_df, x='yearmonth', y='count', label='Total Users', marker='o')
sns.lineplot(data=monthly_users_df, x='yearmonth', y='unregistered', label='Unregistered Users', marker='o')
sns.lineplot(data=monthly_users_df, x='yearmonth', y='registered', label='Registered Users', marker='o')

ax.set(title="Tren pengguna sepeda", xlabel='Bulan-Tahun', ylabel='Total user')
ax.legend()
# Display the plot
st.pyplot(fig)

# Visualization in the first column
st.header("Visualizations")

# Example definition, adjust based on your data
grouped_hour_custom = main_df.groupby(['weekday', 'hour']).agg({
    'count_x': 'mean',  # Ubah 'average_counts' menjadi nama kolom yang benar 'count_x'
}).reset_index()

st.write("<div style='font-size: 24px;'>Bagaimana pola rata-rata jumlah peminjaman sepeda per jam berubah antara hari kerja dan akhir pekan?</div>", unsafe_allow_html=True)
with st.expander("Lihat Visualisasi"):
    fig, ax = plt.subplots(figsize=(12, 8))
    for workingday, group in grouped_hour_custom.groupby('weekday'):
        day_type = 'Hari Kerja' if workingday else 'Akhir Pekan'
        hours_np = group['hour'].to_numpy()
        counts_np = group['count_x'].to_numpy()  # Ubah 'average_counts' menjadi nama kolom yang benar 'count_x'
        ax.plot(hours_np, counts_np, label=f'Jenis Hari: {day_type}', color=('pink' if workingday else 'cyan'))
    ax.set_xlabel('Jam')
    ax.set_ylabel('Rata-rata Jumlah Peminjaman Sepeda')
    ax.set_title('Rata-rata Jumlah Peminjaman Sepeda per Jam Berdasarkan Hari Kerja dan Akhir Pekan')
    plt.legend(title='Jenis Hari', loc='upper right', labels=['Hari Kerja', 'Akhir Pekan']) 
    st.pyplot(fig)
    st.write("Dari visualisasi di atas, terlihat pola rata-rata jumlah peminjaman sepeda per jam berubah antara hari kerja dan akhir pekan.")

grouped_season_year = main_df.groupby(['season_x', 'year']).agg({
    'count_x': 'mean',
    # Tambahkan kolom lain yang diperlukan di sini
}).reset_index()

st.write("<div style='font-size: 24px;'>Apakah ada perbedaan pola peminjaman sepeda di musim panas, gugur, musim dingin, dan musim semi?</div>", unsafe_allow_html=True)
with st.expander("Lihat Visualisasi"):
        fig, ax = plt.subplots(figsize=(12, 8))
        bar_width = 0.2
        bar_positions = np.arange(len(grouped_season_year['year'].unique()))
        for i, (season, group) in enumerate(grouped_season_year.groupby('season_x')):
            ax.bar(bar_positions + (i * bar_width), group['count_x'], width=bar_width, label=f'Musim: {season}', alpha=0.7)
        ax.set_xlabel('Tahun')
        ax.set_ylabel('Rata-rata Jumlah Peminjaman Sepeda')
        ax.set_title('Rata-rata Jumlah Peminjaman Sepeda per Tahun Berdasarkan Musim')
        ax.set_xticks(bar_positions + (bar_width * (len(grouped_season_year['season_x'].unique()) - 1) / 2))
        ax.set_xticklabels(grouped_season_year['year'].unique())
        ax.legend(title='Musim', loc='upper right')
        st.pyplot(fig)
        st.write("Dari visualisasi di atas, terlihat perbedaan pola peminjaman sepeda di musim panas, gugur, musim dingin, dan musim semi.")

grouped_month_2011 = main_df[main_df['year'] == 2011].groupby(['month_x', 'year']).agg({
    'count_x': 'mean',
    # Tambahkan kolom lain yang diperlukan di sini
}).reset_index()

grouped_month_2012 = main_df[main_df['year'] == 2012].groupby(['month_x', 'year']).agg({
    'count_x': 'mean',
    # Tambahkan kolom lain yang diperlukan di sini
}).reset_index()

st.write("<div style='font-size: 24px;'>Bagaimana tingkat peminjaman sepeda berubah sepanjang bulan (tahun 2011-2012)?</div>", unsafe_allow_html=True)
with st.expander("Lihat Visualisasi"):
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(grouped_month_2011['month_x'].to_numpy(), grouped_month_2011['count_x'].to_numpy(), marker='o', linestyle='-', color='purple', label='2011')
        ax.plot(grouped_month_2012['month_x'].to_numpy(), grouped_month_2012['count_x'].to_numpy(), marker='o', linestyle='-', color='magenta', label='2012')
        ax.set_xlabel('Bulan')
        ax.set_ylabel('Rata-rata Jumlah Peminjaman Sepeda')
        ax.set_title('Perubahan Rata-rata Jumlah Peminjaman Sepeda sepanjang Bulan (Tahun 2011-2012)')
        plt.legend(title='Tahun', loc='upper right')
        st.pyplot(fig)
        st.write("Dari visualisasi di atas, terlihat tingkat peminjaman sepeda berubah sepanjang bulan (tahun 2011-2012).")

# Menambahkan informasi kredit
st.markdown(
    "<div style='text-align: center;'><h5 style='color: #888;'>Copyright ©, created by Kinanthi Putri Ariyani</h5></div>",
    unsafe_allow_html=True
)
