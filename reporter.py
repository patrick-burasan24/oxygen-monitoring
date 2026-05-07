import os
from dotenv import load_dotenv
import datetime as dt
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import database as db

if __name__ == "__main__":
    load_dotenv("./data.env")

    DATABASE_PATH = os.getenv("DATABASE_PATH")
    if DATABASE_PATH is None:
        print("Couldn't find database path. Exiting here.")
        exit(1)

    con = db.initialize_db(DATABASE_PATH)
    daily_stats = db.summary(con)
    con.close()

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html")
    html_string = template.render(
        date_today=dt.datetime.today().strftime("%B %d, %Y"),
        stats=daily_stats
    )

    with open("Daily_Report.pdf", "w+b") as pdf_file:
        pisa.CreatePDF(html_string, dest=pdf_file)
