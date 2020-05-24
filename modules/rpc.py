from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import configparser
import logging
import os
import uuid
import re
from datetime import datetime
from decimal import Decimal

from logging.handlers import TimedRotatingFileHandler

import modules.db
import modules.translations as translations

# Set logging info
logger = logging.getLogger("rpc_log")
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler('{}/logs/{:%Y-%m-%d}-rpc.log'.format(os.getcwd(), datetime.now()),
                                   when="d",
                                   interval=1,
                                   backupCount=5)
logger.addHandler(handler)

# Read config and parse constants
config = configparser.ConfigParser()
config.read('{}/webhookconfig.ini'.format(os.getcwd()))


# Check the currency of the bot
CURRENCY = config.get('main', 'currency')
URL = config.get('routes', '{}_url'.format(CURRENCY))

# DB connection settings
WALLET_IP = config.get(CURRENCY, 'wallet_ip')
WALLET_PORT = config.get(CURRENCY, 'wallet_port')
WALLET_USERNAME = config.get(CURRENCY, 'wallet_username')
WALLET_PASSWORD = config.get(CURRENCY, 'wallet_password')
MIN_TX_CONFIRMATION = config.get(CURRENCY, 'min_tx_confirmation')

CURRENCY_NAME = config.get(CURRENCY, 'currency_name')
CURRENCY_SYMBOL = config.get(CURRENCY, 'currency_symbol')

# Constants
RE_EMOJI = re.compile('[\U00010000-\U0010ffff\U000026A1]', flags=re.UNICODE)

rpc = AuthServiceProxy("http://%s:%s@%s:%s"%(WALLET_USERNAME, WALLET_PASSWORD, WALLET_IP, WALLET_PORT))


def strip_emoji(text):
    """
    Remove Emojis from tweet text to prevent issues with logging
    """
    logger.info('{}: removing emojis'.format(datetime.now()))
    text = str(text)
    return RE_EMOJI.sub(r'', text)

def get_account_balance(account_name):
    """
    Get the current balance of an account
    """
    unconfirmed_balance = rpc.getbalance(account_name, 1)
    confirmed_balance = rpc.getbalance(account_name, int(MIN_TX_CONFIRMATION))
    return {
        "balance": confirmed_balance,
        "pending": unconfirmed_balance - confirmed_balance,
    }

def validate_address(address):
    """
    Validate that the provided address is possible
    """
    logger.info("{}: validate address {}".format(datetime.now(), address))

    result = rpc.validateaddress(address)

    logger.info("{}: got {}".format(datetime.now(), result))

    return result["isvalid"]

def generate_new_account():
    """
    Generate a new account
    """
    while True:
        account_name = str(uuid.uuid1()).replace("-", "")
        result = rpc.getaddressesbyaccount(account_name)
        if len(result) == 0:
            address = rpc.getnewaddress(account_name)
            return {
                "account": account_name,
                "address": address,
            }

def send_tip(message, users_to_tip, tip_index):
    """
    Process tip for specified user
    """
    bot_status = config.get('main', 'bot_status')
    if bot_status == 'maintenance':
        modules.social.send_dm(message['sender_id'], translations.maintenance_text[message['language']],
                               message['from_app'])
        return
    else:
        logger.info("{}: sending tip to {}".format(datetime.now(), users_to_tip[tip_index]['receiver_screen_name']))
        if str(users_to_tip[tip_index]['receiver_id']) == str(message['sender_id']):
            modules.social.send_reply(message,
                                      translations.self_tip_text[message['language']].format(CURRENCY_SYMBOL,
                                                                                             message['from_app']))

            logger.info("{}: User tried to tip themself").format(datetime.now())
            return

        # Check if the receiver has an account
        receiver_account_get = ("SELECT account FROM users where user_id = {} and users.from_app = '{}'"
                                .format(int(users_to_tip[tip_index]['receiver_id']), message['from_app']))
        receiver_account_data = modules.db.get_db_data(receiver_account_get)

        # If they don't, check reserve accounts and assign one.
        if not receiver_account_data:
            receiver_account_info = modules.db.create_account(users_to_tip[tip_index]['receiver_id'], message['from_app'], users_to_tip[tip_index]['receiver_screen_name'], 0)
            users_to_tip[tip_index]['receiver_account'] = receiver_account_info["account"]
            logger.info("{}: Sender sent to a new receiving account.  Created  account {}"
                        .format(datetime.now(), users_to_tip[tip_index]['receiver_account']))

        else:
            users_to_tip[tip_index]['receiver_account'] = receiver_account_data[0][0]

        # Send the tip
        if message['from_app'] == 'telegram':
            message['tip_id'] = "{}-{}-{}{}".format(message['from_app'], message['chat_id'], message['id'], tip_index)
        else:
            message['tip_id'] = "{}-{}{}".format(message['from_app'], message['id'], tip_index)

        logger.info("{}: {} - Sending Tip:".format(datetime.now(), message['tip_id']))
        logger.info("{}: {} - From: {}".format(datetime.now(), message['tip_id'], message['sender_account']))
        logger.info("{}: {} - To: {}".format(datetime.now(), message['tip_id'], users_to_tip[tip_index]['receiver_account']))
        logger.info("{}: {} - amount: {:8f}".format(datetime.now(), message['tip_id'], message['tip_amount_raw']))

        try:
            move(message['sender_account'], users_to_tip[tip_index]['receiver_account'], float("{:8f}".format(message['tip_amount_raw'])))
        except:
            modules.social.send_reply(message, 'There was an error processing one of your tips.  '
                                            'Please reach out to the admin with this code: {}'
                                        .format(message['tip_id']))
            return


        # Update the DB
        message['text'] = strip_emoji(message['text'])
        modules.db.set_db_data_tip(message, users_to_tip, tip_index)

        # Get receiver's new balance
        try:
            logger.info("{}: Checking to receive new tip")

            balance_return = get_account_balance(users_to_tip[tip_index]['receiver_account'])
            users_to_tip[tip_index]['balance'] = balance_return['balance']

            modules.social.send_dm(users_to_tip[tip_index]['receiver_id'],
                                translations.receiver_tip_text[users_to_tip[tip_index]['receiver_language']]
                                .format(message['sender_screen_name'], message['tip_amount_raw'],
                                        CURRENCY_SYMBOL, CURRENCY_NAME, URL), message['from_app'])

        except Exception as e:
            logger.info("{}: ERROR IN RECEIVING NEW TIP - POSSIBLE NEW ACCOUNT NOT REGISTERED WITH DPOW: {}"
                         .format(datetime.now(), e))

        logger.info("{}: tip sent to {}".format(datetime.now(), users_to_tip[tip_index]['receiver_screen_name']))

def move(from_account, to_account, amount):
    rpc.move(from_account, to_account, float("{:8f}".format(amount)))

def send_from(from_account, to_address, amount):
    return rpc.sendfrom(from_account, to_address, float("{:8f}".format(amount)))
