import datetime

def actual_date_time():
    now = datetime.datetime.now()
    date_server = now.strftime("%d.%m.%Y")
    time_server = now.strftime("%H:%M")
    time_with_sec = now.strftime("%H:%M:%S")
    return time_server, date_server, time_with_sec