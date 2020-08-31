from datetime import datetime


def get_time():
    current_datetime = datetime.now()
    datetime_prefix = current_datetime.strftime('%y_%m_%d_%H_%M_%S')
    datetime_dict = {
        'year': current_datetime.year,
        'month': current_datetime.month,
        'day': current_datetime.day,
        'hour': current_datetime.hour,
        'minute': current_datetime.minute,
        'second': current_datetime.second
    }
    return datetime_prefix, datetime_dict
