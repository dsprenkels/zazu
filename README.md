# zazu
Twitter bot in Python3 for populating my own timeline with texts from a text file.

## Etymology

`zazu` was named after Zazu, the hornbill from Disney's The Lion King.

## Requirements

 * python3
 * python-twitter (`pip install python-twitter`)
 * API keys from [Twitter](https://apps.twitter.com/)
 
## Setup

 * Clone this repo
 * Create a plain text source file to store your tweets.
 * Copy sampleconfig.txt to config.txt and enter your preferred settings. At the very least, submit valid Twitter API keys and point to your source file.
 * Fill your source file with a few tweets.
 * [Optional] Run `python3 zazu.py` to post your first tweet as a test run.
 * Make a cron-job for zazu.
