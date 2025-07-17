import datetime

def date_to_utc_midnight_unix_timestamp(date: datetime.date) -> int:
    """
    Returns a unix timestamp representing the given date at UTC 00:00:00
    Last docstring edit: -FoxyHunter V4.3.0
    Last method edit: -FoxyHunter V4.3.0
    :param date:
    :return: int
    """
    return int(datetime.datetime.combine(
        date, datetime.time.min,
        datetime.timezone.utc
    ).timestamp())

def time_to_utc_at_epoch_timestamp(time: datetime.time) -> int:
    """
    Returns a unix timestamp representing the given time in UTC at epoch
    Last docstring edit: -FoxyHunter V4.3.0
    Last method edit: -FoxyHunter V4.3.0
    :param date:
    :return: int
    """
    return int(datetime.datetime.combine(
        datetime.date(1970, 1, 1),
        time,
        datetime.timezone.utc
    ).timestamp())