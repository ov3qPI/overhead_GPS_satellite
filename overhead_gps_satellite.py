from skyfield.api import load, Topos
import os
import time
import requests

def is_tle_outdated(filename, max_age_seconds):
    """Check if the TLE file is older than the allowed age in seconds."""
    if not os.path.exists(filename):
        return True  # File doesn't exist; it needs to be downloaded
    # Check the file's last modified time
    file_age_seconds = time.time() - os.path.getmtime(filename)
    return file_age_seconds > max_age_seconds

def download_tle(url, filename):
    """Download the TLE file and save it locally."""
    print(f"Downloading updated TLE data from {url}...")
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    with open(filename, 'w') as file:
        file.write(response.text)
    print(f"TLE data saved to {filename}.")

def main():
    # Constants
    TLE_URL = 'https://celestrak.org/NORAD/elements/gps-ops.txt'
    LOCAL_TLE_FILE = 'gps-ops.txt'
    TLE_MAX_AGE_SECONDS = 7 * 24 * 60 * 60  # Update every 7 days

    # Check if TLE file exists and is up-to-date
    if is_tle_outdated(LOCAL_TLE_FILE, TLE_MAX_AGE_SECONDS):
        download_tle(TLE_URL, LOCAL_TLE_FILE)
    else:
        print(f"TLE file {LOCAL_TLE_FILE} is up-to-date.")

    # Load the necessary data from Skyfield
    ts = load.timescale()
    eph = load('de421.bsp')  # Ephemeris file
    satellites = load.tle_file(LOCAL_TLE_FILE)  # Load TLE from local file
    print(f'Loaded {len(satellites)} GPS satellites.')

    # Observer's location (change to your desired coordinates)
    observer = Topos(latitude_degrees=38.478752, longitude_degrees=-107.877739)

    try:
        print("\n" * 3)  # Reserve space for three lines of dynamic output

        while True:
            # Get the current time
            t = ts.now()

            # Calculate altitudes for all GPS satellites
            max_altitude = -90
            best_satellite = None
            for sat in satellites:
                difference = sat - observer  # Calculate difference between satellite and observer
                topocentric = difference.at(t)  # Compute the position at the given time
                alt, az, distance = topocentric.altaz()  # Calculate alt, az, distance

                if alt.degrees > max_altitude:
                    max_altitude = alt.degrees
                    best_satellite = sat

            # Display the satellite most directly overhead
            if best_satellite:
                print("\033[F\033[K" * 3, end="")  # Move up 3 lines and clear them
                print(f"Satellite overhead: {best_satellite.name}")
                print(f"Altitude: {max_altitude:.2f}°")
                print(f"Azimuth: {az.degrees:.2f}°")

            time.sleep(1)  # Update every second

    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()