import openpyxl
import time
import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

now = datetime.datetime.now()
current_month = str(now.strftime("%m")).lstrip("0")
current_day = str(now.strftime("%d")).lstrip("0")
print(current_month, current_day)

WEBHOOK_URL = os.getenv("BIRTHDAY_WEBHOOK_URL")


def find_birthdays(month, day, spreadsheet):
    wb = openpyxl.load_workbook(spreadsheet)
    ws = wb.active

    for row in ws.iter_rows(values_only=True):
        if row[1] == str(month) and row[2] == str(day):
            print(f'Happy Birthday <@{row[0]}>!')
            message = {"content": 'Happy Birthday <@{}>!'.format(row[0])}
            send_birthday = requests.post(url=WEBHOOK_URL, data=message)
            time.sleep(3)


find_birthdays(current_month, current_day, "birthdays.xlsx")