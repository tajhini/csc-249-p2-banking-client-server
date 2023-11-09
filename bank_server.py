#!/usr/bin/env python3
#
# Bank Server application
# Jimmy da Geek

import socket
import selectors
import sys
import re
import types


ALL_ACCOUNTS = dict()   # initialize an empty dictionary
ACCT_FILE = "accounts.txt"
sel = selectors.DefaultSelector()
client_dict = dict()


##########################################################
#                                                        #
# Bank Server Core Functions                             #
#                                                        #
# No Changes Needed in This Section                      #
#                                                        #
##########################################################

def acctNumberIsValid(ac_num):
    """Return True if ac_num represents a valid account number. This does NOT test whether the account actually exists, only
    whether the value of ac_num is properly formatted to be used as an account number.  A valid account number must be a string,
    lenth = 8, and match the format AA-NNNNN where AA are two alphabetic characters and NNNNN are five numeric characters."""
    return isinstance(ac_num, str) and \
        len(ac_num) == 8 and \
        ac_num[2] == '-' and \
        ac_num[:2].isalpha() and \
        ac_num[3:8].isdigit()

def acctPinIsValid(pin):
    """Return True if pin represents a valid PIN number. A valid PIN number is a four-character string of only numeric characters."""
    return (isinstance(pin, str) and \
        len(pin) == 4 and \
        pin.isdigit())

def amountIsValid(amount):
    """Return True if amount represents a valid amount for banking transactins. For an amount to be valid it must be a positive float()
    value with at most two decimal places."""
    return isinstance(amount, float) and (round(amount, 2) == amount) and (amount >= 0)

class BankAccount:
    """BankAccount instances are used to encapsulate various details about individual bank accounts."""
    acct_number = ''        # a unique account number
    acct_pin = ''           # a four-digit PIN code represented as a string
    acct_balance = 0.0      # a float value of no more than two decimal places
    
    def __init__(self, ac_num = "zz-00000", ac_pin = "0000", bal = 0.0):
        """ Initialize the state variables of a new BankAccount instance. """
        if acctNumberIsValid(ac_num):
            self.acct_number = ac_num
        if acctPinIsValid(ac_pin):
            self.acct_pin = ac_pin
        if amountIsValid(bal):
            self.acct_balance = bal

    def deposit(self, amount):
        """ Make a deposit. The value of amount must be valid for bank transactions. If amount is valid, update the acct_balance.
        This method returns three values: self, success_code, current balance.
        Success codes are: 020: valid result; 021: invalid amount given. """
        result_code = "020"
        if not amountIsValid(amount):
            result_code = "021"
        else:
            # valid amount, so add it to balance and set succes_code 1
            self.acct_balance += amount
        return self, result_code, round(self.acct_balance,2)

    def withdraw(self, amount):
        """ Make a withdrawal. The value of amount must be valid for bank transactions. If amount is valid, update the acct_balance.
        This method returns three values: self, success_code, current balance.
        Success codes are: 020: valid result; 021: invalid amount given; 022: attempted overdraft. """
        result_code = "020"
        if not amountIsValid(amount):
            # invalid amount, return error 
            result_code = "021"
        elif amount > self.acct_balance:
            # attempted overdraft
            result_code = "022"
        else:
            # all checks out, subtract amount from the balance
            self.acct_balance -= amount
        return self, result_code, round(self.acct_balance,2)

def get_acct(acct_num):
    """ Lookup acct_num in the ALL_ACCOUNTS database and return the account object if it's found.
        Return False if the acct_num is invalid. """
    if acctNumberIsValid(acct_num) and (acct_num in ALL_ACCOUNTS):
        return ALL_ACCOUNTS[acct_num]
    else:
        return False

def load_account(num_str, pin_str, bal_str):
    """ Load a presumably new account into the in-memory database. All supplied arguments are expected to be strings. """
    try:
        # it is possible that bal_str does not represent a float, so be sure to catch that error.
        bal = float(bal_str)
        if acctNumberIsValid(num_str):
            if get_acct(num_str):
                print(f"Duplicate account detected: {num_str} - ignored")
                return False
            # We have a valid new account number not previously loaded
            new_acct = BankAccount(num_str, pin_str, bal)
            # Add the new account instance to the in-memory database
            ALL_ACCOUNTS[num_str] = new_acct
            print(f"loaded account '{num_str}'")
            return True
    except ValueError:
        print(f"error loading acct '{num_str}': balance value not a float")
    return False
    
def load_all_accounts(acct_file = "accounts.txt"):
    """ Load all accounts into the in-memory database, reading from a file in the same directory as the server application. """
    print(f"loading account data from file: {acct_file}")
    with open(acct_file, "r") as f:
        while True:
            line = f.readline()
            if not line:
                # we're done
                break
            if line[0] == "#":
                # comment line, no error, ignore
                continue
            # convert all alpha characters to lowercase and remove whitespace, then split on comma
            acct_data = line.lower().replace(" ", "").split(',')
            if len(acct_data) != 3:
                print("ERROR: invalid entry in account file: '{line}' - IGNORED")
                continue
            load_account(acct_data[0], acct_data[1], acct_data[2])
    print("finished loading account data")
    return True

##########################################################
#                                                        #
# Bank Server Network Operations                         #
#                                                        #
#                                                        #
#                                                        #
##########################################################

def validate_user_info(acct_num, acct_pin, key):
    """ Validates the account information is received in the correct format. Validates the account number an daccount pin in the correct format. """
    # receives account information; account number and account pin split by "|"
    
    account = get_acct(acct_num)
    

    if (client_duplicate_log(key, acct_num) == False):

        if (account != False):
            if (account.acct_pin == acct_pin):
                #client_acct_num.append(account.acct_number)
                return "VALID"
            else:
                #Account number and PIN do not match.
                return "ERR: NOMATCH"
        else:
            #Account doesn't exist.
            return "ERR: NOT FND"
    else:
        close_conn(key)


def accept_wrapper(sock):
    client_conn, client_addy = sock.accept()
    print(f"Accepted connection from {client_conn} at {client_addy}.")
    client_conn.setblocking(False)
    data = types.SimpleNamespace(addr = client_addy, inb=b"", outb =b"")
    sel.register(client_conn, selectors.EVENT_READ , data=data)
   

def bal_req(acct_num):
    client_acct = get_acct(acct_num)
    if client_acct != False:
        client_bal = str(client_acct.acct_balance)
        return client_bal

def deposit_req(acct_num, client_deposit):
        bal_req(acct_num)
        client_acct = get_acct(acct_num)
        # Validates client deposit amount
        if (client_deposit.isnumeric()):
            if (client_acct):
                client_acct, result, new_bal = (client_acct.deposit(float(client_deposit)))
                # Deposit amount validated; success
                if (result == "020"):
                    return str(new_bal)
                # Deposit amount validated; failure
                elif(result == "021"):
                    # Failure by result of incorrect deposit amount format
                    return "ERR: FORMAT"
        else: 
            # Deposit amount != numbers
            return "ERR: FORMAT"


def withdrawl_req(acct_num, client_withdraw):
        bal_req(acct_num)
        client_acct = get_acct(acct_num)
        if (client_withdraw.isnumeric()):
            if (client_acct):
                client_acct, result, new_bal = (client_acct.withdraw(float(client_withdraw)))
                # Withdrawal amount validated; success
                if (result == "020"):
                    return str(new_bal)
                # Withdrawal amount validated; failure
                elif(result == "021"):
                    # Failure by result of incorrect withdrawl amount format
                    return "ERR: FORMAT"

                elif(result == "022"):
                    # Failure by overdraft request
                    return "ERR: OVERDRAFT"
        else: 
            # Deposit amount != numbers
            return "ERR: FORMAT"


def process_msg(msg, key):
    client_conn = key.fileobj


    login_reg = r"[L][O][G]\s[a-z]{2}-\d{5}\s\d{4}"
    bal_code = "BAL"
    withdrw_reg = r"[W][D]\s\d+"
    dep_reg = r"[D][E][P]\s\d+"
    exit_code = "EXIT"
    #login
    if (re.search(login_reg, msg)):
        msg = msg.split(" ")
        acct_num = msg[1]
        acct_pin = msg[2]
        validation = validate_user_info(acct_num, acct_pin, key)
        return validation
    #Balance
    elif (msg == bal_code):
        client_acct_num = list(client_dict.keys())[list(client_dict.values()).index(client_conn)]
        return bal_req(client_acct_num)
    #Withdraw
    elif (re.search(withdrw_reg, msg)):
        msg = msg.split(" ")
        amt = msg[1]
        client_acct_num = list(client_dict.keys())[list(client_dict.values()).index(client_conn)]
        new_bal = withdrawl_req(client_acct_num, amt)
        return new_bal
    #Deposit
    elif (re.search(dep_reg, msg)):
        msg = msg.split(" ")
        amt = msg[1]
        client_acct_num = list(client_dict.keys())[list(client_dict.values()).index(client_conn)]
        new_bal = deposit_req(client_acct_num, amt)
        return new_bal

    #exit 
    elif(msg == exit_code):
        close_conn(key)
   
    else:
        return "ERR: NOTRECOG"
    #not recognised

def close_conn(key) :
    client_conn = key.fileobj
    data = key.data
    client_acct_num = list(client_dict.keys())[list(client_dict.values()).index(client_conn)]
    client_dict.pop(client_acct_num)
    print(f"Closing connection to {data.addr}")
    sel.unregister(client_conn)
    client_conn.close()  

def transaction(key):
        client_conn = key.fileobj
        client_message = client_conn.recv(1024)  # Should be ready to read
        if client_message:
            processed_data = process_msg(client_message.decode("utf-8"), key)
            if (processed_data):
                client_conn.sendall(processed_data.encode("utf-8"))
        else:
            close_conn(key)

def connect_obj(key, acct_num):
    client_conn = key.fileobj
    client_dict[acct_num] = client_conn


def client_duplicate_log(key, acct_num):
    all_accts_active = list(client_dict.keys())
    if (acct_num in all_accts_active):
        return True
    else:
        connect_obj(key, acct_num)
        return False

    


def run_network_server():
    """ Runs the server.
    """
    # Gets the ip address of the local machine.
    try:
        host = socket.gethostbyname(socket.gethostname())
        port = 65432
    except socket.gaierror:
        print('Could not get hostname...Ending server.')
        sys.exit()
        
    # Creates a socket
    print(f"Server is starting - listening for connections at IP, {host}, and port, {port}")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv_sock:
            # Binds the  socket to the specified address and port above
            serv_sock.bind((host, port))
            # Listening for incoming connections
            serv_sock.listen()
            print(f"Listening on {host}:{port}")

            serv_sock.setblocking(False)
            sel.register(serv_sock, selectors.EVENT_READ, data=None)
            
            try:
                while True:
                    events = sel.select(timeout=None)
                    for key, mask in events:
                        if key.data is None:
                            accept_wrapper(key.fileobj)
                        else:
                            transaction(key)
            except KeyboardInterrupt:
                print("Caught keyboard interrupt, exiting")
            finally:
                sel.close()

    except Exception as e:
        sys.exit()
    

##########################################################
#                                                        #
# Bank Server Demonstration                              #
#                                                        #
# Demonstrate basic server functions.                    #
# No changes needed in this section.                     #
#                                                        #
##########################################################

# def demo_bank_server():
#     """ A function that exercises basic server functions and prints out the results. """
#     # get the demo account from the database
#     acct = get_acct("zz-99999")
#     print(f"Test account '{acct.acct_number}' has PIN {acct.acct_pin}")
#     print(f"Current account balance: {acct.acct_balance}")
#     print(f"Attempting to deposit 123.45...")
#     _, code, new_balance = acct.deposit(123.45)
#     if not code:
#         print(f"Successful deposit, new balance: {new_balance}")
#     else:
#         print(f"Deposit failed!")
#     print(f"Attempting to withdraw 123.45 (same as last deposit)...")
#     _, code, new_balance = acct.withdraw(123.45)
#     if not code:
#         print(f"Successful withdrawal, new balance: {new_balance}")
#     else:
#         print("Withdrawal failed!")
#     print(f"Attempting to deposit 123.4567...")
#     _, code, new_balance = acct.deposit(123.4567)
#     if not code:
#         print(f"Successful deposit (oops), new balance: {new_balance}")
#     else:
#         print(f"Deposit failed as expected, code {code}") 
#     print(f"Attempting to withdraw 12345.45 (too much!)...")
#     _, code, new_balance = acct.withdraw(12345.45)
#     if not code:
#         print(f"Successful withdrawal (oops), new balance: {new_balance}")
#     else:
#         print(f"Withdrawal failed as expected, code {code}")
#     print("End of demo!")

##########################################################
#                                                        #
# Bank Server Startup Operations                         #
#                                                        #
# No changes needed in this section.                     #
#                                                        #
##########################################################

if __name__ == "__main__":
    # on startup, load all the accounts from the account file
    load_all_accounts(ACCT_FILE)
    # uncomment the next line in order to run a simple demo of the server in action
    #demo_bank_server()
    run_network_server()
    print("bank server exiting...")

  