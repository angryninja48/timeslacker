import os

from app import TimeSheet

TS_USER = os.getenv("TS_USER")
TS_PASSWORD = os.getenv("TS_PASSWORD")

def main():
    worked_days = ['Tuesday', 'Wednesday', 'Thursday']
    non_worked_days = list(DAYS - set(worked_days))

    time = TimeSheet(username=TS_USER,password=TS_PASSWORD,days=worked_days,non_worked_days=non_worked_days, headless=False)
    submit = time.run()

if __name__ == "__main__":
    main()
