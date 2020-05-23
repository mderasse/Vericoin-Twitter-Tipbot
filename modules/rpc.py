from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import configparser
import logging
import os
import uuid 

# Read config and parse constants
config = configparser.ConfigParser()
config.read('{}/webhookconfig.ini'.format(os.getcwd()))

# Check the currency of the bot
CURRENCY = config.get('main', 'currency')

# DB connection settings
WALLET_IP = config.get(CURRENCY, 'wallet_ip')
WALLET_PORT = config.get(CURRENCY, 'wallet_port')
WALLET_USERNAME = config.get(CURRENCY, 'wallet_username')
WALLET_PASSWORD = config.get(CURRENCY, 'wallet_password')
MIN_TX_CONFIRMATION = config.get(CURRENCY, 'min_tx_confirmation')


rpc = AuthServiceProxy("http://%s:%s@%s:%s"%(WALLET_USERNAME, WALLET_PASSWORD, WALLET_IP, WALLET_PORT))

def get_account_balance(account_name):
    """
    Get the current balance of an account
    """
    unconfirmed_balance = rpc.getbalance(account_name, 1)
    confirmed_balance = rpc.getbalance(account_name, MIN_TX_CONFIRMATION)
    return {
        "balance": confirmed_balance,
        "pending": unconfirmed_balance - confirmed_balance,
    }

def validate_address(address):
    """
    Validate that the provided address is possible
    """
    result = rpc.validateaddress(address)

    return result["isvalid"] == 'true'

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
    # bot_status = config.get('main', 'bot_status')
    # if bot_status == 'maintenance':
    #     modules.social.send_dm(message['sender_id'], translations.maintenance_text[message['language']],
    #                            message['from_app'])
    #     return
    # else:
    #     logger.info("{}: sending tip to {}".format(datetime.now(), users_to_tip[tip_index]['receiver_screen_name']))
    #     if str(users_to_tip[tip_index]['receiver_id']) == str(message['sender_id']):
    #         modules.social.send_reply(message,
    #                                   translations.self_tip_text[message['language']].format(CURRENCY.upper(),
    #                                                                                          message['from_app']))

    #         logger.info("{}: User tried to tip themself").format(datetime.now())
    #         return

    #     # Check if the receiver has an account
    #     receiver_account_get = ("SELECT account FROM users where user_id = {} and users.from_app = '{}'"
    #                             .format(int(users_to_tip[tip_index]['receiver_id']), message['from_app']))
    #     receiver_account_data = modules.db.get_db_data(receiver_account_get)

    #     # If they don't, check reserve accounts and assign one.
    #     if not receiver_account_data:
    #         users_to_tip[tip_index]['receiver_account'] = modules.db.get_spare_account()
    #         create_receiver_account = ("INSERT INTO users (user_id, from_app, user_name, account, register) "
    #                                    "VALUES(%s, %s, %s, %s, 0)")
    #         create_receiver_account_values = [users_to_tip[tip_index]['receiver_id'], message['from_app'],
    #                                           users_to_tip[tip_index]['receiver_screen_name'],
    #                                           users_to_tip[tip_index]['receiver_account']]
    #         modules.db.set_db_data(create_receiver_account, create_receiver_account_values)
    #         logger.info("{}: Sender sent to a new receiving account.  Created  account {}"
    #                      .format(datetime.now(), users_to_tip[tip_index]['receiver_account']))

    #     else:
    #         users_to_tip[tip_index]['receiver_account'] = receiver_account_data[0][0]

    #     # Send the tip
    #     if message['from_app'] == 'telegram':
    #         message['tip_id'] = "{}-{}-{}{}".format(message['from_app'], message['chat_id'], message['id'], tip_index)
    #     else:
    #         message['tip_id'] = "{}-{}{}".format(message['from_app'], message['id'], tip_index)

    #     # work = get_pow(message['sender_account'])
    #     work = get_pow_debug(message)
    #     logger.info("{}: {} - Sending Tip:".format(datetime.now(), message['tip_id']))
    #     logger.info("{}: {} - From: {}".format(datetime.now(), message['tip_id'], message['sender_account']))
    #     logger.info("{}: {} - To: {}".format(datetime.now(), message['tip_id'], users_to_tip[tip_index]['receiver_account']))
    #     logger.info("{}: {} - amount: {:f}".format(datetime.now(), message['tip_id'], message['tip_amount_raw']))
    #     logger.info("{}: {} - work: {}".format(datetime.now(), message['tip_id'], work))
    #     if work == '':
    #         logger.info("{}: processed without work".format(datetime.now()))
    #         send_data = {
    #             'action': 'send',
    #             'wallet': WALLET,
    #             'source': message['sender_account'],
    #             'destination': users_to_tip[tip_index]['receiver_account'],
    #             'amount': int(message['tip_amount_raw']),
    #             'id': 'tip-{}'.format(message['tip_id'])
    #         }
    #         json_request = json.dumps(send_data)
    #         r = requests.post('{}'.format(NODE_IP), data=json_request)
    #         rx = r.json()
    #         logger.info("{}: {} - send return: {}".format(datetime.now(), message['tip_id'], rx))
    #         if 'block' in rx:
    #             message['send_hash'] = rx['block']
    #         else:
    #             modules.social.send_reply(message, 'There was an error processing one of your tips.  '
    #                                                'Please reach out to the admin with this code: {}'
    #                                       .format(message['tip_id']))
    #             return

    #     else:
    #         logger.info("{}: processed with work: {}".format(datetime.now(), work))
    #         send_data = {
    #             'action': 'send',
    #             'wallet': WALLET,
    #             'source': message['sender_account'],
    #             'destination': users_to_tip[tip_index]['receiver_account'],
    #             'amount': int(message['tip_amount_raw']),
    #             'id': 'tip-{}'.format(message['tip_id']),
    #             'work': work
    #         }
    #         logger.info("{}: send data: {}".format(datetime.now(), send_data))
    #         json_request = json.dumps(send_data)
    #         r = requests.post('{}'.format(NODE_IP), data=json_request)
    #         rx = r.json()
    #         logger.info("{}: {} - send return: {}".format(datetime.now(), message['tip_id'], rx))
    #         if 'block' in rx:
    #             message['send_hash'] = rx['block']
    #         else:
    #             modules.social.send_reply(message, 'There was an error processing one of your tips.  '
    #                                                'Please reach out to the admin with this code: {}'
    #                                       .format(message['tip_id']))
    #             return

    #     # Update the DB
    #     message['text'] = strip_emoji(message['text'])
    #     modules.db.set_db_data_tip(message, users_to_tip, tip_index)

    #     # Get receiver's new balance
    #     try:
    #         logger.info("{}: Checking to receive new tip")

    #         receive_pending(users_to_tip[tip_index]['receiver_account'])
    #         balance_return = rpc.account_balance(account="{}".format(users_to_tip[tip_index]['receiver_account']))
    #         users_to_tip[tip_index]['balance'] = balance_return['balance']
    #         # create a string to remove scientific notation from small decimal tips
    #         if str(users_to_tip[tip_index]['balance'])[0] == ".":
    #             users_to_tip[tip_index]['balance'] = "0{}".format(str(users_to_tip[tip_index]['balance']))
    #         else:
    #             users_to_tip[tip_index]['balance'] = str(users_to_tip[tip_index]['balance'])

    #         # Send a DM to the receiver.  Twitter is removed due to spam issues.
    #         if message['from_app'] != 'twitter':
    #             modules.social.send_dm(users_to_tip[tip_index]['receiver_id'],
    #                                    translations.receiver_tip_text[users_to_tip[tip_index]['receiver_language']]
    #                                    .format(message['sender_screen_name'], message['tip_amount_text'],
    #                                            CURRENCY.upper(), CURRENCY.upper(), URL), message['from_app'])

    #     except Exception as e:
    #         logger.info("{}: ERROR IN RECEIVING NEW TIP - POSSIBLE NEW ACCOUNT NOT REGISTERED WITH DPOW: {}"
    #                      .format(datetime.now(), e))

    #     logger.info(
    #         "{}: tip sent to {} via hash {}".format(datetime.now(), users_to_tip[tip_index]['receiver_screen_name'],
    #                                                 message['send_hash']))
