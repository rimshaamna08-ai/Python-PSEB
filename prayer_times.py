'''Assignment 1: to get todays namaz timing for any city and
 for how long until the next prayer'''


import json #imports built in JSON tools
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import urllib.error
import urllib.parse
import urllib.request


API_URL = "https://api.aladhan.com/v1/timingsByCity"
PRAYERS = ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha")
CALCULATION_METHOD = 2


def fetch_prayer_data(city, country, date=None, timeout=10):
    """Fetch prayer times and location metadata from Aladhan."""
    params = {
        "city": city,
        "country": country,
        "method": CALCULATION_METHOD,
    }
    endpoint = API_URL if date is None else f"{API_URL}/{date}"
    url = f"{endpoint}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "PrayerTimesCLI/1.0"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            if not 200 <= status_code < 300:
                print(f"HTTP error {status_code} while calling API.")
                return None

            payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, dict):
                print("API returned an invalid response.")
                return None
            if payload.get("code") != 200:
                print(f"API returned non-200 status code: {payload.get('code')}")
                return None

            data = payload.get("data")
            if not isinstance(data, dict):
                print("API response is missing prayer-time data.")
                return None
            if not isinstance(data.get("timings"), dict):
                print("API response is missing prayer timings.")
                return None
            if not isinstance(data.get("meta"), dict):
                print("API response is missing location metadata.")
                return None
            return data

    except urllib.error.HTTPError as e:
        print(f"HTTP error: {e.code} - {e.reason}")
        return None
    except urllib.error.URLError as e:
        if isinstance(e.reason, TimeoutError):
            print(f"Request timed out after {timeout} seconds.")
        else:
            print(f"Network error: {e.reason}")
        return None
    except TimeoutError:
        print(f"Request timed out after {timeout} seconds.")
        return None
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        print(f"Could not read the API response: {e}")
        return None

def get_next_prayer(timings, now):
    """Return the next prayer name and its local datetime."""
    upcoming = []
    for prayer in PRAYERS:
        prayer_time = datetime.strptime(timings[prayer].split()[0], "%H:%M").time()
        prayer_datetime = datetime.combine(now.date(), prayer_time).replace(
            tzinfo=now.tzinfo
        )
        if prayer_datetime > now:
            upcoming.append((prayer_datetime, prayer))

    if upcoming:
        prayer_datetime, prayer = min(upcoming)
        return prayer, prayer_datetime

    fajr_time = datetime.strptime(timings["Fajr"].split()[0], "%H:%M").time()
    tomorrow_fajr = datetime.combine(
        now.date() + timedelta(days=1), fajr_time
    ).replace(tzinfo=now.tzinfo)
    return "Fajr", tomorrow_fajr

def main():
    city = input("Enter city: ").strip()
    country = input("Enter country: ").strip()

    if not city or not country:
        print("City and country are required.")
        return

    print(f"Fetching prayer times for {city}, {country}...")
    data = fetch_prayer_data(city, country)
    if data is None:
        print("Unable to fetch prayer times.")
        return

    timezone_name = data["meta"].get("timezone")
    if not isinstance(timezone_name, str) or not timezone_name:
        print("The API did not provide a timezone for this location.")
        return

    try:
        city_timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        print(f"Unknown timezone returned by API: {timezone_name}")
        return

    now = datetime.now(city_timezone)
    today = now.strftime("%d-%m-%Y")
    date_data = data.get("date")
    gregorian_date = (
        date_data.get("gregorian") if isinstance(date_data, dict) else None
    )
    api_date = (
        gregorian_date.get("date") if isinstance(gregorian_date, dict) else None
    )
    if api_date != today:
        data = fetch_prayer_data(city, country, date=today)
        if data is None:
            print("Unable to fetch prayer times for the local date.")
            return

    timings = data["timings"]
    try:
        for prayer in PRAYERS:
            if not isinstance(timings.get(prayer), str):
                print(f"API response is missing a valid {prayer} time.")
                return

        print(f"\nPrayer times for {city}, {country} on {now:%A, %d %B %Y}:")
        for prayer in PRAYERS:
            print(f"{prayer}: {timings[prayer]}")

        next_prayer, next_time = get_next_prayer(timings, now)
    except (KeyError, ValueError, IndexError, TypeError) as e:
        print(f"Could not interpret the prayer times returned by the API: {e}")
        return

    remaining_minutes = int((next_time - now).total_seconds() // 60)
    hours, minutes = divmod(remaining_minutes, 60)
    print(f"\nNext prayer: {next_prayer} at {next_time:%H:%M}")
    print(f"Time remaining: {hours} hour(s), {minutes} minute(s)")


if __name__ == "__main__":
    main()
