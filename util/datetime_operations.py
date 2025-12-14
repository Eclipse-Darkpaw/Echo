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


def get_current_artfight_day(
    start_date: datetime.date,
    prompt_time: datetime.time | None,
    now_utc: datetime.datetime | None = None
) -> int:
    """
    Calculate the current artfight day based on when prompts drop, not calendar date.
    
    The day increments when the prompt drops (at prompt_time), not at midnight UTC.
    For example, if prompt_time is 19:00 UTC and it's currently 18:00 UTC on day 3,
    we're still on day 2 because day 3's prompt hasn't dropped yet.
    
    :param start_date: The start date of artfight
    :param prompt_time: The time when prompts drop (assumed UTC). If None, uses midnight.
    :param now_utc: Current UTC datetime. If None, uses current time.
    :return: The current artfight day (1-indexed)
    """
    if now_utc is None:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
    
    current_date = now_utc.date()
    current_time = now_utc.time()
    
    # Calculate the base day from date difference
    days_since_start = (current_date - start_date).days
    
    # If we're before the prompt time today, we're still on "yesterday's" prompt
    if prompt_time and current_time < prompt_time:
        # We haven't had today's prompt yet, so we're still on the previous day
        artfight_day = days_since_start  # Not +1, because today's prompt hasn't dropped
    else:
        # Today's prompt has dropped (or will drop if prompt_time is None)
        artfight_day = days_since_start + 1
    
    # Ensure minimum of 1 (on day 1 before first prompt, still day 1)
    return max(1, artfight_day)