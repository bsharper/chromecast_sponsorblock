# Chromecast SponsorBlock

This project is a simple script to skip sponsor segments on YouTube videos played on a Chromecast device using the SponsorBlock API.

## Installation Guide

### Step 1: Set up a Virtual Environment

1. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

2. Activate the virtual environment:
    - On Windows:
      ```sh
      .\venv\Scripts\activate
      ```
    - On macOS and Linux:
      ```sh
      source venv/bin/activate
      ```

### Step 2: Install Dependencies

1. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

### Step 3: Configure the Chromecast Name

1. Open the `sb_chromecast.py` file in a text editor.
2. Change the `CHROMECAST_NAME` variable to the name of your Chromecast device:
    ```python
    CHROMECAST_NAME = "Your Chromecast Name"
    ```

### Step 4: Run the Script

1. Run the script:
    ```sh
    python sb_chromecast.py
    ```

## Notes

I wrote this for me, it's simple and dumb but it does work and so far nobody has yelled at me for making it. This is similar to another project I made several years ago that does the same thing for Apple TVs.
