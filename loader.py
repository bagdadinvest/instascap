import instaloader
import os
import logging
import csv
import time
import random
import sys

# Initialize Instaloader instance
L = instaloader.Instaloader()

# Set up logging
logging.basicConfig(filename='initial_run_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        logging.debug(f"Creating directory: {path}")
        os.makedirs(path)
    else:
        logging.debug(f"Directory already exists: {path}")

def log_downloaded_file(file_path):
    """Log the downloaded file's path and time."""
    logging.info(f"Downloaded: {file_path}")

def download_user_posts(username):
    """Download the last 50 posts from the given Instagram username."""
    try:
        logging.debug(f"Starting download for {username}...")
        print(f"Starting download for {username}...")

        # Create directories for user and media types
        base_dir = f"downloads/{username}"
        image_dir = f"{base_dir}/images"
        video_dir = f"{base_dir}/videos"

        create_directory(image_dir)
        create_directory(video_dir)

        # Get profile from username
        profile = instaloader.Profile.from_username(L.context, username)

        # Download the latest 50 posts
        total_files = 0
        posts = profile.get_posts()
        for idx, post in enumerate(posts):
            if idx >= 50:  # Limit to last 50 posts
                break

            # Define paths for different file types
            if post.typename == 'GraphImage':  # It's an image post
                target_dir = image_dir
            elif post.typename == 'GraphVideo':  # It's a video post
                target_dir = video_dir
            else:
                target_dir = base_dir  # If it's another type, use the base directory

            # Download post media to the target directory
            L.download_post(post, target=target_dir)

            # Log the downloaded file and path
            for file in os.listdir(target_dir):
                if file.startswith(post.shortcode):
                    file_path = os.path.join(target_dir, file)
                    log_downloaded_file(file_path)
                    total_files += 1
        
        logging.debug(f"Finished downloading for {username}. Total files: {total_files}")
        print(f"Finished downloading for {username}. Total files: {total_files}")

    except Exception as e:
        logging.error(f"Error downloading posts for {username}: {e}")
        print(f"Error downloading posts for {username}: {e}")

def read_usernames_from_csv(file_path):
    """Read Instagram usernames from a CSV file."""
    usernames = []
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:  # Ignore empty rows
                    usernames.append(row[0])
        logging.debug(f"Loaded usernames from CSV: {usernames}")
        print(f"Loaded usernames: {usernames}")
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        print(f"Error reading CSV file: {e}")
    return usernames

def get_user_confirmation(usernames):
    """Ask the user to confirm the list of usernames."""
    print("The following usernames were loaded:")
    for username in usernames:
        print(f"- {username}")
    confirmation = input("Do you want to proceed with these usernames? (yes/no): ").lower()
    if confirmation == 'yes':
        logging.debug("User confirmed the list of usernames.")
        return True
    else:
        logging.debug("User did not confirm the list of usernames.")
        return False

def get_scraping_time_range():
    """Ask the user to input a valid time range for random sleep intervals."""
    while True:
        time_range = input("Enter the random scraping interval in minutes (format: min,max): ")
        try:
            min_time, max_time = map(int, time_range.split(","))
            if min_time < max_time:
                logging.debug(f"User provided valid time range: {min_time} to {max_time} minutes.")
                return min_time * 60, max_time * 60  # Convert minutes to seconds
            else:
                print("Error: The first number must be smaller than the second.")
        except ValueError:
            print("Error: Please enter two numbers separated by a comma.")

def countdown(seconds):
    """Display a countdown timer."""
    while seconds:
        mins, secs = divmod(seconds, 60)
        time_format = f'{mins:02d}:{secs:02d}'
        print(f"Next scrape in: {time_format}", end='\r')
        time.sleep(1)
        seconds -= 1
    print("\nScraping next account...")

if __name__ == "__main__":
    # Read usernames from CSV
    csv_file = 'instagram_usernames.csv'  # Replace with your actual file path
    usernames = read_usernames_from_csv(csv_file)

    if not usernames:
        print("No usernames found in CSV file.")
    else:
        # Confirm usernames with the user
        if not get_user_confirmation(usernames):
            print("User canceled the operation.")
            exit()

        # Get the time range for random sleep intervals
        min_sleep_time, max_sleep_time = get_scraping_time_range()

        # Randomly shuffle usernames for each run
        random.shuffle(usernames)
        print(f"Shuffled usernames: {usernames}")

        # Loop through each username
        for username in usernames:
            print(f"Scraping {username}...")
            download_user_posts(username)

            # Add a random sleep time between each download (human-like behavior)
            sleep_time = random.randint(min_sleep_time, max_sleep_time)  # Random sleep within the user-provided range
            print(f"Waiting for {sleep_time // 60} minutes before scraping the next account...")
            logging.debug(f"Sleeping for {sleep_time} seconds.")

            # Countdown timer for next scrape
            countdown(sleep_time)

        print("Initial scraping completed for all accounts.")
