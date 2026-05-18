import sys
import os
import shutil
import visualizer
import argparse
import database as db
import datetime as dt
from pathlib import Path
from xhtml2pdf import pisa
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from config import get_env, valid_date_format


def get_resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def generate_daily_report(target_date, save_path=None):
    """Generates the PDF report for the specified target_date (YYYY-MM-DD)."""
    if not target_date:
        print("Error: target_date cannot be empty.")
        return False

    if not valid_date_format(target_date):
        print(
            f"Error: {target_date} does not conform to the YYYY-MM-DD date format. Exitting here.")

    print(f"Fetching data for {target_date}...")

    db_path = get_env("DATABASE_PATH", "./sensor_readings.db")
    o2_min_threshold = float(get_env("O2_MIN_THRESHOLD", "19.5"))
    con = db.initialize_db(db_path)

    daily_stats = db.summary(con, target_date)
    if not daily_stats:
        print(f"No data found for {target_date}. Aborting report.")
        return False

    reports_path = Path("reports")
    img_path = Path("img")
    reports_path.mkdir(exist_ok=True)
    img_path.mkdir(exist_ok=True)

    pdf_filename = f"Sensor_Parameter_Report_{target_date}.pdf"

    target_img_dir = img_path / pdf_filename
    if target_img_dir.exists():
        shutil.rmtree(target_img_dir)
    target_img_dir.mkdir(exist_ok=True)

    visualizer.generate_graph(con, target_date, target_img_dir)

    template_dir = get_resource_path("templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report.html")
    display_date = dt.datetime.strptime(
        target_date, "%Y-%m-%d").strftime("%B %d, %Y")

    html_string = template.render(
        date_today=display_date,
        stats=daily_stats,
        o2_graph_path=str((target_img_dir / "o2_levels.png").absolute()),
        temp_graph_path=str((target_img_dir / "internal_temperature.png").absolute()),
        press_graph_path=str((target_img_dir / "internal_pressure.png").absolute()),
        o2_min_threshold=o2_min_threshold,
    )

    if not save_path:
        output_filepath = reports_path / pdf_filename
    else:
        output_filepath = Path(save_path)
    with open(output_filepath, "w+b") as pdf_file:
        pisa.CreatePDF(html_string, dest=pdf_file)

    print("Report created successfully.")
    return True


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
        if not valid_date_format(target_date):
            print(
                f"{target_date} does not conform to the YYYY-MM-DD date format. Exitting here.")
            exit(1)
    else:
        target_date = dt.datetime.today().strftime("%Y-%m-%d")

    generate_daily_report(target_date)
