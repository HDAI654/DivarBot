# Divar Ad Tracker Bot

This is a Telegram bot built with Python that helps users track and manage their advertisements on the Divar website. Users can add, view, and delete their ad titles via simple Telegram commands. The bot also sends scheduled hourly notifications.

## Features
- View the list of your current ads.
- Delete ads via interactive Telegram buttons.
- Scheduled hourly reminders for active users.

## Getting Started

### 1. Install Dependencies

```bash
git clone https://github.com/HDAI654/DivarBot.git
cd DivarBot
```

Make sure you have Python 3.8+ installed. Then install dependencies using:

```bash
npm install -g localtunnel

pip install -r requirements.txt
```

### 2. Start LocalTunnel
In a separate terminal, run the following to expose your local server:
```bash
lt --port 5000 --subdomain diwar
```
This will generate a public webhook URL like:
```bash
https://diwar.loca.lt/
```

### 3. Run the Bot
Now run the bot:
```bash
python main.py
```

### 4. Interact with the Bot on Telegram
Use the following commands:

- /start – Start the bot

- /add – Add a new advertisement (with format:  Divar Page Link - Ad Page Link - Ad Title)

- /my_ads – View your saved ads

- /delete – Delete an ad using a selection menu

## Performance Video
You can see the performance of the bot in the following video:

https://drive.google.com/file/d/1NjV8XMMlUxAFDHGk2tB2KWK3c6ZKE0R9/view?usp=sharing

## Important Note
You must create the .env file in root of project
with this format :
```bash
BOT_TOKEN=your_bot_token
PORT=the_port_that_you_run_localtunnel
INTERVAL=the_scraper_interval_in_seconds
DATA_FILE=address_of_json_file_for_saving_data
AD_THRESHOLD=the_threshold_of_ads_that_you_want_to_get_warning
```

## LICENSE
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.