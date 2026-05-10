import os
from dotenv import load_dotenv
import datetime as dt
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import database as db
import argparse
import visualizer
import shutil

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="O2 Sensor Report Wizard")
    parser.add_argument(
        "-d", "--date",
        type=str,
        help="Target date must be given in the format YYYY-MM-DD. Default to current system date",
        default=None
    )
    args = parser.parse_args()

    if args.date:
        target_date = args.date.strip()
    else:
        target_date = dt.datetime.today().strftime("%Y-%m-%d")

    print(f"Fetching data for {target_date}...")

    load_dotenv("./data.env")
    DATABASE_PATH = os.getenv("DATABASE_PATH")
    if DATABASE_PATH is None:
        print("Couldn't find database path. Exiting here.")
        exit(1)

    con = db.initialize_db(DATABASE_PATH)
    daily_stats = db.summary(con, target_date)

    if daily_stats is None:
        print(f"No data found for {target_date}. Aborting report.")
        exit(0)

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html")
    display_date = dt.datetime.strptime(target_date, "%Y-%m-%d").strftime("%B %d, %Y")

    os.makedirs("./reports/", exist_ok=True)
    os.makedirs("./img/", exist_ok=True)
    pdf_filename = f"Sensor_Parameter_Report_{target_date}.pdf"
    if os.path.exists(f"./img/{pdf_filename}/"):
        shutil.rmtree(f"./img/{pdf_filename}/")
    os.makedirs(f"./img/{pdf_filename}/", exist_ok=True)
    visualizer.generate_graph(con, target_date, pdf_filename)

    html_string = template.render(
        date_today=display_date,
        stats=daily_stats,
        o2_graph_path=f"./img/{pdf_filename}/o2_levels.png",
        temp_graph_path=f"./img/{pdf_filename}/internal_temperature.png",
        press_graph_path=f"./img/{pdf_filename}/internal_pressure.png",
    )

    with open(f"./reports/{pdf_filename}", "w+b") as pdf_file:
        pisa.CreatePDF(html_string, dest=pdf_file)
    
    print("Report created successfully. Program has exitted.")
