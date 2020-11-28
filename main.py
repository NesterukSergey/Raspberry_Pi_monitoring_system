#!/usr/bin/python

# import sys
# print(sys.executable)

from monitoring_system.utils import read_json, get_serial_number, write_txt
from monitoring_system.scheduler.Scheduler import Scheduler


if __name__ == '__main__':
    main_config = read_json('./configs/main.json')
    scheduler = Scheduler(main_config=main_config)
    write_txt('serial_number.txt', get_serial_number())
    scheduler.start()
