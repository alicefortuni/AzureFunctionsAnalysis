import seaborn as sns
import pandas as pd
import warnings
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

warnings.filterwarnings("ignore")
pd.set_option('display.expand_frame_repr', False)
plt.rcParams.update({'figure.figsize': (12, 7)})

# Load data
csv_file_path = 'dataset/azure_functions_invocation_trace.csv'
data = pd.read_csv(csv_file_path)

# Show info about data
print(f"\nDataset info:")
data.info()
print(f"\nHead of dataset:\n{data.head()}\n")

# Convert timestamp to datetime
data['end_timestamp'] = pd.to_datetime(data['end_timestamp'], unit='s')
new_start_date = pd.Timestamp('2021-01-31')
time_shift = new_start_date - data['end_timestamp'].min()
data['end_timestamp'] = data['end_timestamp'] + time_shift
data['hour'] = data['end_timestamp'].dt.hour
data['day_of_week'] = data['end_timestamp'].dt.dayofweek
data['date'] = data['end_timestamp'].dt.date

# Duration of invocations
duration_statistics = data['duration'].describe()
print(f"\nStatistics for duration of the invocations:\n{duration_statistics}\n")

sns.histplot(data['duration'], bins=50, stat='probability', edgecolor='black')
plt.title('Distribution of invocation durations')
plt.xlabel('Duration (sec)')
plt.ylabel('Frequency of invocations')
plt.show()


### Analysis of invocations by date###
color_day = {
    0: '#FF6347',
    1: '#4682B4',
    2: '#3CB371',
    3: '#FFD700',
    4: '#DA70D6',
    5: '#FF4500',
    6: '#1E90FF'
}

fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 8))
date_counts = data['date'].value_counts().sort_index()
df = pd.DataFrame(data.set_index('date').loc[date_counts.index]['day_of_week'])

df['data'] = df.index
df = df.drop_duplicates(subset='data')
bar_colors = [color_day[day] for day in df['day_of_week']]
axes[0].bar(date_counts.index, date_counts.values, color=bar_colors)
axes[0].set_title('Distribution of invocations by Date')
axes[0].set_xlabel('Date')
axes[0].set_ylabel('Number of Invocations')
axes[0].tick_params(axis='x', rotation=45)

daily_duration = data.groupby('date')['duration'].mean().reset_index()
sns.lineplot(x='date', y='duration', data=daily_duration, ax=axes[1])
axes[1].set_title('Average duration of invocations by Date')
axes[1].set_xlabel('Date')
axes[1].set_ylabel('Average duration (sec)')
axes[1].tick_params(axis='x', rotation=45)


handles = [plt.Line2D([0], [0], color=color, lw=4) for color in color_day.values()]
labels = color_day.keys()
fig.legend(handles, labels, title='Day of week', loc='upper right')

plt.tight_layout()
plt.show()


print(f"\nStatistics for distribution invocation durations for day 2021-02-12:\n{data[(data['date'] == pd.to_datetime('2021-02-12').date())]['duration'].describe()}\n")
sns.boxplot(x='date', y='duration', data=data)
plt.title('Distribution of invocation durations by Date')
plt.xlabel('Date')
plt.ylabel('Duration (sec)')
plt.tick_params(axis='x', rotation=45)
plt.show()

sns.boxplot(x='date', y='duration', data=data)
plt.title('Distribution of invocation durations by Date (with log scale)')
plt.xlabel('Date')
plt.ylabel('Duration (sec)')
plt.yscale('log')
plt.tick_params(axis='x', rotation=45)
plt.show()


### Analysis of  invocations by hour###

fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 8))
hourly_mean = data.groupby('hour')['date'].count() / data['date'].nunique()
axes[0].bar(hourly_mean.index, hourly_mean.values, color='blue')
axes[0].set_title('Average daily invocations by Hour of Day')
axes[0].set_xlabel('Hour of the day')
axes[0].set_ylabel('Average Daily Invocations')
axes[0].set_xticks(range(0, 24))
axes[0].set_xlim(-0.5, len(hourly_mean)-0.5)

hourly_duration = data.groupby('hour')['duration'].mean().reset_index()
sns.lineplot(x='hour', y='duration', data=hourly_duration, ax=axes[1])
axes[1].set_title('Average duration of invocations by Hour of Day')
axes[1].set_xlabel('Hour of the day')
axes[1].set_ylabel('Average duration (sec)')
axes[1].set_xticks(range(0, 24))
axes[1].set_xlim(-0.5, len(hourly_duration)-0.5)

plt.tight_layout()
plt.show()

print(f"\nStatistics for distribution invocation durations for Hour 22:\n{data[(data['hour'] == 22)].describe()}\n")
sns.boxplot(x='hour', y='duration', data=data)
plt.title('Distribution of invocation duration by Hour of Day')
plt.xlabel('Hour of Day')
plt.ylabel('Duration (sec)')
plt.xticks(range(0, 24))
plt.show()

sns.boxplot(x='hour', y='duration', data=data)
plt.title('Distribution of invocation duration by Hour of Day (with log scale)')
plt.xlabel('Hour of Day')
plt.ylabel('Duration (sec)')
plt.xticks(range(0, 24))
plt.yscale('log')
plt.show()

### Applications and functions ###

# Ranaming of applications
app_names = data['app'].unique()
rename_map = {app: f'app_{i+1}' for i, app in enumerate(app_names)}
data['app'] = data['app'].replace(rename_map)

print(f"Number of unique applications: {data['app'].nunique()}")
unique_functions = data[['app', 'func']].drop_duplicates()
print(f"Total number of unique functions (considering app-function combinations): {unique_functions.shape[0]}")

#Distribution of the number of functions per application
functions_per_app = data.groupby('app')['func'].nunique().reset_index()
functions_per_app.columns = ['app', 'num_functions']
data = pd.merge(data, functions_per_app, on='app', how='left')
print(f"\nDescriptive statistics on the number of functions per application:\n{functions_per_app['num_functions'].describe()}\n")
sns.countplot(x='num_functions', data=functions_per_app)
plt.title('Distribution of the number of functions per application')
plt.xlabel('Number of Functions')
plt.ylabel('Number of Applications')
plt.show()

#Applications vs Mean of invocations
invocations_per_app_per_day = data.groupby(['app', 'date']).size()
mean_invocations_per_app = invocations_per_app_per_day.groupby('app').mean()
mean_invocations_per_app_sorted = mean_invocations_per_app.sort_values(ascending=False)
mean_invocations_per_app_sorted.plot(kind='bar', title='Applications vs Daily mean of invocations')
plt.xlabel('Application')
plt.ylabel('Daily mean of invocations')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# Visualizzazione della relazione tra durata media e numero di funzioni
app_duration = data.groupby('app')['duration'].mean().reset_index() # Calcolo della durata media delle invocazioni per applicazione
app_analysis = pd.merge(app_duration, functions_per_app, on='app')
print(app_analysis)

sns.scatterplot(x='num_functions', y='duration', data=app_analysis)
plt.title('Relationship between Number of functions and Average invocation duration per Application')
plt.xlabel('Number of functions')
plt.ylabel('Average invocation duration per Application (sec)')
plt.show()

correlation = app_analysis['duration'].corr(app_analysis['num_functions'])
print(f'Correlation between average duration and number of functions: {correlation:.4f}')

#Analisi della durate delle invocazioni per ogni applicazione

average_duration_per_function = data.groupby(['app', 'func'])['duration'].mean().reset_index()

plt.scatter(average_duration_per_function['app'], average_duration_per_function['duration'], color='blue', alpha=0.7)
plt.title('Average duration of individual functions per application')
plt.xlabel('Application')
plt.ylabel('Average Duration of Individual Functions (sec)')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

plt.show()



def visualizza_pattern(target_app):
    df_app = data[data['app'] == target_app]
    functions_names = df_app['func'].unique()
    rename2_map = {app: f'fun_{i + 1}' for i, app in enumerate(functions_names)}
    df_app['func'] = df_app['func'].replace(rename2_map)
    df_app['end_timestamp_sec'] = df_app['end_timestamp'].astype(np.int64) // 10 ** 9
    df_app['start_timestamp_sec'] = df_app['end_timestamp_sec'] - df_app['duration']
    df_app['start_timestamp'] = pd.to_datetime(df_app['start_timestamp_sec'], unit='s')

    fig1 = plt.figure(figsize=(10, 8))
    ax1 = fig1.add_subplot(111)
    ax1.set_title(f"Temporal Pattern of Function invocations for Application: {target_app}")
    ax1.set_xlabel("Init timestamp")
    ax1.set_ylabel("Function")
    df_app_sorted = df_app.sort_values(by='start_timestamp')
    ax1.scatter(df_app_sorted['start_timestamp'], df_app_sorted['func'], marker='o',
               label='Invocations')
    ax1.set_yticks(range(len(df_app_sorted['func'].unique())))
    ax1.set_yticklabels(df_app_sorted['func'].unique())
    ax1.legend()

    fig2 = plt.figure(figsize=(10, 8))
    ax2 = fig2.add_subplot(111)
    ax2.boxplot([df_app[df_app['func'] == func]['duration'] for func in df_app['func'].unique()],
                labels=df_app['func'].unique())
    ax2.set_xlabel("Function")
    ax2.set_ylabel("Duration of Invocations (sec)")
    ax2.set_title("Distribution of the duration of invocations by Function")

    plt.tight_layout()
    plt.show()



def select_application():
    def show_graph():
        selected_app = app_combobox.get()
        visualizza_pattern(selected_app)
    # Main window
    root = tk.Tk()
    root.title("Select an application")
    root.geometry("800x600")
    # Frame principale
    root.geometry('800x600')
    app_names = data[data['num_functions'] > 1]['app'].unique()
    app_combobox = ttk.Combobox(root, values=list(app_names), width=50)
    app_combobox.pack()

    show_button = tk.Button(root, text='Show graphs', command=show_graph)
    show_button.pack()

    root.mainloop()

# Start GUI
select_application()
