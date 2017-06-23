#!/usr/bin/env python3

import argparse
import logging
import configparser
import twitter
import random
import time
import os
import re
import sys


INITIAL_LOGLEVEL = logging.INFO
CONFIGFILE = "config.ini"
RANDOMTIME = 5 * 60 # 5 minutes


def isValidTweet(text):
    text = text.strip()
    relative_length = len(text)
    for match in re.findall("https?://[\S]*",text):
        relative_length = relative_length + 23 - len(match)
    return relative_length <= 140 and relative_length > 0

def isEmpty(filename):
    filestat = os.stat(SOURCEFILENAME)
    return filestat.st_size == 0

def get_api():
    CONFIG = configparser.ConfigParser()
    CONFIG.read(CONFIGFILE)
    api = twitter.Api(
        consumer_key=CONFIG.get('api', 'consumer_key'),
        consumer_secret=CONFIG.get('api', 'consumer_secret'),
        access_token_key=CONFIG.get('api', 'access_token_key'),
        access_token_secret=CONFIG.get('api', 'access_token_secret')
    )
    return api

def main(configfile, logfile, sourcefilename, verbosity):
    # read configfile
    config = configparser.ConfigParser()
    config.read_file(configfile)

    # enable logging
    logging.basicConfig(format='%(asctime)s %(levelname)s: zazu %(message)s',
        stream=logfile,level=verbosity)

    tweettext = ""
    while(not isValidTweet(tweettext) and not isEmpty(SOURCEFILENAME)):
        # open linefile, read first line
        sourcefile = open(SOURCEFILENAME,"r")
        tweettext = sourcefile.readline().strip()

        # read the tail of the source file, close the file
        sourcefile_tail = sourcefile.read()
        sourcefile.close()

        # process tweet
        if isValidTweet(tweettext):
            logging.info("Valid tweet text: \"%s\"", tweettext)
            print(tweettext)
            try:
                api = get_api()
                api.VerifyCredentials()
            except twitter.error.TwitterError as error:
                logging.error("TwitterError: %s",error)
                return # do not update the source file
            except Exception as error:
                logging.error("%s: %s",type(error),error)
                return # do not update the source file
            randomtime = random.randrange(0,config.get('general','random_time',fallback=RANDOMTIME))
            logging.info("sleeping for %d seconds (%.2f minutes) before posting tweet",randomtime,randomtime / 60)
            time.sleep(300)
            try:
                post_update = api.PostUpdate(tweettext,trim_user=True,verify_status_length=True)
            except Exception as error:
                logging.error("%s: %s",type(error),error)
                return # do not update the source file
            logging.info("tweeted %s at %s",post_update.text,post_update.created_at)
            logging.debug("full post_update info: %s",str(post_update))

        else:
            logging.error("\"%s\" is not a valid tweet",tweettext)
            print("\"" + tweettext + "\"","is an unvalid tweet text")

        # update source file
        sourcefile = open(SOURCEFILENAME,"w")
        sourcefile.write(sourcefile_tail)
        sourcefile.close()


if __name__ == "__main__":
    def ExistingFilePath(filename):
        if not os.path.isfile(filename):
            raise argparse.ArgumentTypeError("'%s' is not a file" % filename)
        else:
            return filename

    # Initialize the argument parser
    parser = argparse.ArgumentParser(
        prog="python3 zazu.py",
        description="@jd7h's personal Twitter bot")
    parser.add_argument("--config",
        help="path to a different zazu configuration file (defaults to %s)" % CONFIGFILE,
        type=argparse.FileType('r'),
        default=CONFIGFILE)
    parser.add_argument("--logfile",
        help="write the logs to this file (defaults to standard error)",
        type=argparse.FileType('w'),
        default=sys.stderr)
    parser.add_argument("tweetsfile",
        help="file containing the tweets (default)",
        type=ExistingFilePath)
    parser.add_argument('--verbose', '-v', action='count',
        help="be (more) verbose",
        default=0)
    parser.add_argument('--quiet', '-q', action='count',
        help="suppress output",
        default=0)
    args = parser.parse_args()

    # Parse the command line arguments
    main(
        configfile=args.config,
        logfile=args.logfile,
        sourcefilename=args.tweetsfile,
        verbosity=INITIAL_LOGLEVEL + 10 * (args.verbose - args.quiet),
    )
