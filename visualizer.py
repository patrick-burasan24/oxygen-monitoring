import database as db
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_parameter(parameter, timestamps, color, label, pdf_filename, name):
    start_time = timestamps[0]
    end_time = timestamps[-1]
    start_num = mdates.date2num(start_time)
    end_num = mdates.date2num(end_time)

    fig, ax = plt.subplots(figsize=(10, 5))

    locator = mdates.HourLocator(interval=2)
    interval_ticks = locator.tick_values(start_time, end_time)
    all_ticks = sorted(list(set(interval_ticks) | {start_num, end_num}))
    ax.set_xticks(all_ticks)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_xlim(start_time, end_time)

    ax.plot(timestamps, parameter, color=color, linewidth=2, label=label)
    plt.xticks(rotation=45)
    plt.savefig(f"./img/{pdf_filename}/{name}.png")
    plt.close(fig)

def generate_graph(con, target_date, pdf_filename):
    if con is None:
        return
    
    if target_date is None:
        target_date = dt.datetime.today().strftime("%Y-%m-%d")
    
    daily_timeseries = db.get_daily_timeseries(con, target_date)
    if daily_timeseries is None:
        print(f"No data found for {target_date}. Aborting graph creation.")
        return
    
    timestamps = []
    o2_levels = []
    temperatures = []
    pressures = []

    for (timestamp, o2, temp, press) in daily_timeseries:
        timestamps.append(dt.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"))
        o2_levels.append(o2)
        temperatures.append(temp)
        pressures.append(press)

    if len(timestamps) == 0:
        return

    plot_parameter(o2_levels, timestamps, "red", "O_2%", pdf_filename, "o2_levels")
    plot_parameter(temperatures, timestamps, "blue", "T", pdf_filename, "internal_temperature")
    plot_parameter(pressures, timestamps, "green", "P", pdf_filename, "internal_pressure")
        
if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(10, 5))
    x_times = ["08:00", "08:10", "08:20"]
    y_oxygen = [20.9, 20.8, 20.9]
    ax.plot(x_times, y_oxygen, color="blue", linewidth=2, label="O2 %")
    plt.savefig("./reports/o2_graph.png", dpi=300)
    plt.close(fig)