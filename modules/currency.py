import configparser
import json
import logging
import os
import re
from datetime import datetime
from decimal import Decimal

import requests
from logging.handlers import TimedRotatingFileHandler

import modules.db
import modules.social
import modules.translations as translations

# Set Log File
logger = logging.getLogger("currency_log")
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler('{}/logs/{:%Y-%m-%d}-currency.log'.format(os.getcwd(), datetime.now()),
                                   when="d",
                                   interval=1,
                                   backupCount=5)
logger.addHandler(handler)

# Read config and parse constants
config = configparser.ConfigParser()
config.read('{}/webhookconfig.ini'.format(os.getcwd()))

# Check the currency of the bot
CURRENCY = config.get('main', 'currency')


def get_fiat_conversion(symbol, fiat_amount):
    """
    Get the current fiat price conversion for the provided fiat:crypto pair
    """
    fiat = convert_symbol_to_fiat(symbol)
    if fiat == 'UNSUPPORTED':
        return -1
    crypto_currency = CURRENCY.lower()
    fiat = fiat.lower()
    post_url = 'https://api.coingecko.com/api/v3/coins/{}'.format(crypto_currency)
    try:
        # Retrieve price conversion from API
        response = requests.get(post_url)
        response_json = json.loads(response.text)
        price = Decimal(response_json['market_data']['current_price'][fiat])
        # Find value of 0.01 in the retrieved crypto
        penny_value = Decimal(0.01) / price
        # Find precise amount of the fiat amount in crypto
        precision = 1
        crypto_value = Decimal(fiat_amount) / price
        # Find the precision of 0.01 in crypto
        crypto_convert = precision * penny_value
        while Decimal(crypto_convert) < 1:
            precision *= 10
            crypto_convert = precision * penny_value
        # Round the expected amount to the nearest 0.01
        temp_convert = crypto_value * precision
        temp_convert = str(round(temp_convert))
        final_convert = Decimal(temp_convert) / Decimal(str(precision))

        return final_convert
    except Exception as e:
        logger.info("{}: Exception converting fiat price to crypto price".format(datetime.now()))
        logger.info("{}: {}".format(datetime.now(), e))
        raise e


def convert_symbol_to_fiat(symbol):
    if symbol == '$':
        return 'USD'
    elif symbol == '€':
        return 'EUR'
    elif symbol == '£':
        return 'GBP'
    else:
        return 'UNSUPPORTED'


def get_fiat_price(fiat):
    fiat = fiat.upper()
    crypto_currency = CURRENCY.upper()
    post_url = 'https://min-api.cryptocompare.com/data/price?fsym={}&tsyms={}'.format(crypto_currency, fiat)
    try:
        # Retrieve price conversion from API
        response = requests.get(post_url)
        response_json = json.loads(response.text)
        price = response_json['{}'.format(fiat)]

        return price
    except Exception as e:
        logger.info("{}: Exception converting fiat price to crypto price".format(datetime.now()))
        logger.info("{}: {}".format(datetime.now(), e))
        raise e