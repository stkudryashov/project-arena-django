from datetime import datetime
from datetime import timedelta
from datetime import time

send_t = datetime(2022, 6, 30, 2, 00)

t_end = time(hour=21, minute=0)
t_start = time(hour=9, minute=0)

if t_end.hour < t_start.hour:
    dt_end = datetime(send_t.year, send_t.month, send_t.day, t_end.hour, t_end.minute)
    dt_start = datetime(send_t.year, send_t.month, send_t.day, t_start.hour, t_start.minute)
else:
    if send_t.hour > t_end.hour:
        dt_end = datetime(send_t.year, send_t.month, send_t.day, t_end.hour, t_end.minute)
        dt_start = datetime(send_t.year, send_t.month, send_t.day, t_start.hour, t_start.minute) + timedelta(days=1)
    else:
        dt_end = datetime(send_t.year, send_t.month, send_t.day, t_end.hour, t_end.minute) - timedelta(days=1)
        dt_start = datetime(send_t.year, send_t.month, send_t.day, t_start.hour, t_start.minute)

if dt_end < send_t < dt_start:
    print('Перенос')
    print(dt_end, send_t, dt_start, sep=' | ')
else:
    print('Все ок')
    print(dt_end, send_t, dt_start, sep=' | ')
