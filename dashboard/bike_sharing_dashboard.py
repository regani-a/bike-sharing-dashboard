import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set style for seaborn
sns.set(style='darkgrid')

# Load datasets
day_df = pd.read_csv("./data/day.csv")
hour_df = pd.read_csv("./data/hour.csv")

# Data Preprocessing
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Function to create daily summary
def create_daily_summary(df):
    daily_summary = df.groupby(df['dteday'].dt.date).agg({
        'cnt': 'sum',
        'temp': 'mean',
        'hum': 'mean'
    }).reset_index()
    daily_summary.rename(columns={'dteday': 'date'}, inplace=True)
    return daily_summary

# Create daily summary DataFrame
daily_summary = create_daily_summary(day_df)

# Streamlit Sidebar
st.sidebar.header("Pengaturan Dashboard")
st.sidebar.subheader("Filter Tanggal")
min_date = daily_summary['date'].min()
max_date = daily_summary['date'].max()
# Get date input
selected_dates = st.sidebar.date_input("Rentang Tanggal", [min_date, max_date])

# Handle single date selection
if len(selected_dates) == 1:
    start_date = pd.Timestamp(selected_dates[0])  # Convert to Timestamp
    end_date = pd.Timestamp(selected_dates[0])    # Use the same date for end_date
else:
    start_date, end_date = pd.Timestamp(selected_dates[0]), pd.Timestamp(selected_dates[1])  # Convert both to Timestamp


# Ensure 'date' in daily_summary is of datetime type
daily_summary['date'] = pd.to_datetime(daily_summary['date'])

# Filter DataFrame based on selected dates
filtered_daily_summary = daily_summary[(daily_summary['date'] >= start_date) & 
                                       (daily_summary['date'] <= end_date)]

# Title
st.title("Dashboard Peminjaman Sepeda")

# Question 1: Jumlah peminjaman harian
st.subheader("Jumlah Peminjaman Harian")
st.write(f"Jumlah total peminjaman sepeda dari {start_date.date()} hingga {end_date.date()} adalah {filtered_daily_summary['cnt'].sum()}")

# Visualization of daily bike rentals
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=filtered_daily_summary, x='date', y='cnt', marker='o', ax=ax)
ax.set_title('Jumlah Peminjaman Sepeda Harian')
ax.set_xlabel('Tanggal')
ax.set_ylabel('Jumlah Peminjaman')
plt.xticks(rotation=45)
st.pyplot(fig)

# Question 2: Pengaruh Suhu terhadap Jumlah Peminjaman
st.subheader("Pengaruh Suhu terhadap Jumlah Peminjaman")
fig, ax = plt.subplots(figsize=(12, 6))
sns.scatterplot(data=filtered_daily_summary, x='temp', y='cnt', ax=ax)
ax.set_title('Pengaruh Suhu terhadap Jumlah Peminjaman')
ax.set_xlabel('Suhu (Normalisasi)')
ax.set_ylabel('Jumlah Peminjaman')
st.pyplot(fig)

correlation = filtered_daily_summary[['temp', 'cnt']].corr().iloc[0, 1]
st.write(f"Koefisien Korelasi antara Suhu dan Jumlah Peminjaman: {correlation:.2f}")

# Additional insights
st.subheader("Insights")
st.write("Berdasarkan visualisasi, terlihat bahwa semakin tinggi suhu, semakin banyak peminjaman sepeda yang terjadi.")

# Temperature Categorization
bins = [-0.10, 0, 0.15, 0.25, 0.35]
labels = ['Very Cold', 'Cool', 'Mild', 'Warm']

hour_df['temp_category'] = pd.cut(hour_df['temp'], bins=bins, labels=labels, include_lowest=True)

filtered_hour_df = hour_df[hour_df['dteday'].dt.date.between(start_date.date(), end_date.date())]

# Grouping data by temperature category
grouped = filtered_hour_df['temp_category'].value_counts().reset_index()
grouped.columns = ['Temperature Category', 'Count']

# Display the grouped data in Streamlit
st.subheader("Total Counts by Temperature Category")
st.write(grouped)

# Visualization
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(grouped['Temperature Category'], grouped['Count'], color='skyblue')
ax.set_title('Total Counts by Temperature Category')
ax.set_xlabel('Temperature Category')
ax.set_ylabel('Total Counts')
plt.xticks(rotation=45)
st.pyplot(fig)

# New Section: Total Peminjaman Berdasarkan Jam
st.subheader("Total Peminjaman Berdasarkan Jam")
filtered_hour_df = hour_df[(hour_df['dteday'] >= start_date) & (hour_df['dteday'] <= end_date)]
hourly_counts = filtered_hour_df.groupby('hr')['cnt'].sum()

# Create the line plot for hourly counts
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(x=hourly_counts.index, y=hourly_counts.values, marker='o', linewidth=2.5, color='dodgerblue')
plt.fill_between(hourly_counts.index, hourly_counts.values, color='lightblue', alpha=0.5)
ax.set_title('Total Peminjaman Sepeda Berdasarkan Jam (Hour Dataset)', fontsize=16)
ax.set_xlabel('Jam', fontsize=14)
ax.set_ylabel('Total Peminjaman', fontsize=14)
plt.xticks(range(0, 24))  # Set x-ticks for every hour
plt.grid(True, linestyle='--', alpha=0.7)
st.pyplot(fig)

# New Section: Total Peminjaman Berdasarkan Musim
st.subheader("Total Peminjaman Berdasarkan Musim")
filtered_day_df = day_df[(day_df['dteday'] >= start_date) & (day_df['dteday'] <= end_date)]
season_counts = filtered_day_df.groupby('season')['cnt'].sum()
season_labels = {1: 'Musim Dingin', 2: 'Musim Semi', 3: 'Musim Panas', 4: 'Musim Gugur'}
season_counts.index = season_counts.index.map(season_labels)

# Create the bar plot for season counts
plt.figure(figsize=(10, 6))
sns.barplot(x=season_counts.index, y=season_counts.values, palette='Blues')
plt.title('Total Peminjaman Sepeda Berdasarkan Musim (Day Dataset)')
plt.xlabel('Musim')
plt.ylabel('Total Peminjaman')
st.pyplot(plt)

# RFM Analysis for Casual Users
filtered_day_df = day_df[(day_df['dteday'] >= start_date) & 
                          (day_df['dteday'] <= end_date)]

st.subheader("RFM Analysis for Casual Users")
casual_rfm = filtered_day_df.groupby(by="dteday").agg({
    "casual": "sum",  
}).reset_index()

casual_rfm.columns = ["last_rental_date", "monetary"]
casual_rfm["frequency"] = casual_rfm["monetary"]  # frequency = total pinjam
recent_date_casual = filtered_day_df['dteday'].max()  # Use filtered data
casual_rfm["recency"] = (recent_date_casual - casual_rfm["last_rental_date"]).dt.days

# Visualization for Casual Users RFM
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))

colors = ["#72BCD4"] * 5

sns.barplot(y="recency", x="last_rental_date", data=casual_rfm.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_title("By Recency (days)", loc="center", fontsize=14)
ax[0].tick_params(axis ='x', labelsize=12)

sns.barplot(y="frequency", x="last_rental_date", data=casual_rfm.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_title("By Frequency", loc="center", fontsize=14)
ax[1].tick_params(axis='x', labelsize=12)

sns.barplot(y="monetary", x="last_rental_date", data=casual_rfm.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_title("By Monetary", loc="center", fontsize=14)
ax[2].tick_params(axis='x', labelsize=12)

plt.suptitle("Best Customer Based on RFM Casual User (last_rental_date)", fontsize=16)
plt.xticks(rotation=45)
st.pyplot(fig)

# RFM Analysis for Registered Users
st.subheader("RFM Analysis for Registered Users")
registered_rfm = filtered_day_df.groupby(by="dteday").agg({
    "registered": "sum",  
}).reset_index()

registered_rfm.columns = ["last_rental_date", "monetary"]
registered_rfm["frequency"] = registered_rfm["monetary"]  # frequency = total pinjam
recent_date_registered = filtered_day_df['dteday'].max()  # Use filtered data
registered_rfm["recency"] = (recent_date_registered - registered_rfm["last_rental_date"]).dt.days

# Visualization for Registered Users RFM
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))

colors = ["#FF7F50"] * 5

sns.barplot(y="recency", x="last_rental_date", data=registered_rfm.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_title("By Recency (days)", loc="center", fontsize=14)
ax[0].tick_params(axis ='x', labelsize=12)

sns.barplot(y="frequency", x="last_rental_date", data=registered_rfm.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_title("By Frequency", loc="center", fontsize=14)
ax[1].tick_params(axis='x', labelsize=12)

sns.barplot(y="monetary", x="last_rental_date", data=registered_rfm.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_title("By Monetary", loc="center", fontsize=14)
ax[2].tick_params(axis='x', labelsize=12)

plt.suptitle("Best Customer Based on RFM Registered User (last_rental_date)", fontsize=16)
plt.xticks(rotation=45)
st.pyplot(fig)

# Conclusion
st.subheader("Kesimpulan")
st.write("Analisis ini menunjukkan bahwa suhu memiliki pengaruh positif terhadap jumlah peminjaman sepeda. Variabel 'temp' dan 'hum' menunjukkan hubungan yang kuat dengan cnt. Semakin tinggi suhu, semakin banyak peminjaman sepeda.")
st.write("Dari dataset day.csv, musim panas menunjukkan total peminjaman tertinggi. Dari dataset hour.csv, peminjaman paling tinggi terjadi pada jam-jam sibuk, seperti pagi dan sore.")
