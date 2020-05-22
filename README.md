# Vericoin /  Verium Twitter & Telegram Tip Bot

Work in Progress

The Tip Bot allows users to send cryptocurrency to users using only their Twitter handle.
That bot is compatible with crypto based on bitcoin such as Vericoin and Verium

Commands

DM Commands: The below commands are handled through sending a DM to @VeriTipBot.

    !help: The tip bot will respond to your DM with a list of commands and their functions. If you forget something, use this to get a hint of how to do it!
    !register: The tip bot will create an account, or validate the account that is currently tied to your Twitter user name. This will return a message containing your account number.
    !balance: Returns the current balance of your account.
    !account: Returns the account number tied to your Twitter user name.
    !withdraw: Withdraws the balance of your tip account to a specified Wallet address. Example: !withdraw VXXXXXXXXXXXXXX will withdraw to account VXXXXXXXXXXXXXX
    !donate: Donates a specified amount from your tip account to the developer. Example: !donate 1 will donate 1 VRC to developers. Thanks for your generosity!


Tweet Commands: Tips are sent through public tweets or retweets. These are processed in real time.

    !tip: Send a tip of a specified amount to a user on Twitter. Example: !tip 1.01 @mderasse will send a 1.01 VRC tip to user @mderasse.


Package Requirement:
- sudo apt-get install libmariadbclient-dev