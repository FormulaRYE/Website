import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as mpl
import scipy.stats as stats
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection

import fastf1 as ff1


def columns():
    df = pd.DataFrame({
        'Column 1': [1, 2, 3, 4],
        'Column 2': [10, 20, 30, 40]
    })

    df


def table():
    dataframe = pd.DataFrame(
        np.random.randn(10, 20),
        columns=('col %d' % i for i in range(20)))

    st.dataframe(dataframe.style.highlight_max(axis=0))


def line_chart():
    chart_data = pd.DataFrame(
         np.random.randn(20, 3),
         columns=['a', 'b', 'c'])

    st.line_chart(chart_data)

def verstappen():
    year = 2021
    wknd = 17
    ses = 'R'
    driver = 'VER'
    colormap = mpl.cm.plasma
    session = ff1.get_session(year, wknd, ses)
    weekend = session.event
    session.load()
    lap = session.laps.pick_driver(driver).pick_lap(2)

    # Get telemetry data
    x = lap.telemetry['X']  # values for x-axis
    y = lap.telemetry['Y']  # values for y-axis
    color = lap.telemetry['Speed']  # value to base color gradient on
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Create the main plot
    fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
    fig.suptitle(f'{weekend.name} {year} - {driver} - Speed', size=24, y=0.97)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
    ax.axis('off')

    # Plot the telemetry data
    ax.plot(lap.telemetry['X'], lap.telemetry['Y'], color='black', linestyle='-', linewidth=16, zorder=0)

    norm = plt.Normalize(color.min(), color.max())
    lc = LineCollection(segments, cmap=colormap, norm=norm, linestyle='-', linewidth=5)
    lc.set_array(color)
    ax.add_collection(lc)

    # Add colorbar
    cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
    normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
    mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap, orientation="horizontal")

    # Render the plot in Streamlit
    st.pyplot(fig)

    # Process telemetry data for multiple laps and show statistics
    def process_lap_range(session, driver, start_lap, end_lap):
        lap_telemetry_set = pd.DataFrame()

        for lap_number in range(start_lap, end_lap + 1):
            lap = session.laps.pick_driver(driver).pick_lap(lap_number)

            if lap is not None:
                lap_telemetry = lap.get_telemetry()  # Ensure telemetry is retrieved correctly

                if not lap_telemetry.empty:
                    lap_telemetry_filtered = lap_telemetry[['X', 'Y', 'Speed']]
                    lap_telemetry_set = pd.concat([lap_telemetry_set, lap_telemetry_filtered], ignore_index=True)
                else:
                    print(f"Telemetry data for lap {lap_number} is empty.")
            else:
                print(f"Lap {lap_number} is not available for driver {driver}.")

        if not lap_telemetry_set.empty:
            average_values = lap_telemetry_set.mean()
            return average_values
        else:
            return None

    # Displaying average telemetry statistics for different laps
    for lap_range in [(1, 10), (11, 29), (30, 56)]:
        start_lap, end_lap = lap_range
        avg_values = process_lap_range(session, driver, start_lap, end_lap)
        if avg_values is not None:
            print(f"Average values for X, Y, and Speed across laps {start_lap}-{end_lap}:")
            print(avg_values)
        else:
            print(f"No telemetry data was found for laps {start_lap}-{end_lap}.")

    # Speed statistics and normal distribution plot
    all_speed_values = lap.telemetry['Speed'].values
    mean_speed = np.mean(all_speed_values)
    std_speed = np.std(all_speed_values)

    speed_range = np.linspace(mean_speed - 3 * std_speed, mean_speed + 3 * std_speed, 100)
    normal_dist = stats.norm.pdf(speed_range, mean_speed, std_speed)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(speed_range, normal_dist, label=f'Normal Distribution. Mean: {mean_speed:.2f}, Std: {std_speed:.2f}',
            color='green')
    ax.fill_between(speed_range, normal_dist, alpha=0.2, color='green')

    ax.set_title(f'Normal Distribution of Speed for {driver} - {weekend.name} {year}')
    ax.set_xlabel('Speed (km/h)')
    ax.set_ylabel('Probability Density')
    ax.legend()

    # Render the distribution plot
    st.pyplot(fig)

if __name__ == '__main__':
    st.title('My first app')
    st.write("Here's our first attempt at using data to create a table:")
    columns()
    st.write("Here's our first attempt at using data to create a line chart:")
    line_chart()
    st.write("Here's our first attempt at using data to create a table:")
    table()
    st.write("Verstappen Things?")
    verstappen()

