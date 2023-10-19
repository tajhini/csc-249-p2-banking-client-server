#!/usr/bin/env python3
#
# Bank Server application
# Jimmy da Geek

import socket
import selectors
import threading
import sys

# HOST = "127.0.0.1"      # Standard loopback interface address (localhost)
# PORT = 65432            # Port to listen on (non-privileged ports are > 1023)
ALL_ACCOUNTS = dict()   # initialize an empty dictionary
ACCT_FILE = "accounts.txt"

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
        Success codes are: 0: valid result; 1: invalid amount given. """
        result_code = 0
        if not amountIsValid(amount):
            result_code = 1
        else:
            # valid amount, so add it to balance and set succes_code 1
            self.acct_balance += amount
        return self, result_code, round(self.acct_balance,2)

    def withdraw(self, amount):
        """ Make a withdrawal. The value of amount must be valid for bank transactions. If amount is valid, update the acct_balance.
        This method returns three values: self, success_code, current balance.
        Success codes are: 0: valid result; 1: invalid amount given; 2: attempted overdraft. """
        result_code = 0
        if not amountIsValid(amount):
            # invalid amount, return error 
            result_code = 1
        elif amount > self.acct_balance:
            # attempted overdraft
            result_code = 2
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
# TODO: THIS SECTION NEEDS TO BE WRITTEN!!               #
#                                                        #
##########################################################

def validate_user_info(client_connection):
    account_info = client_connection.recv(1024)
    #decoded account info
    account_info = account_info.decode("utf-8") # convert bytes to string
    #account number and pin in a list.
    account_info = account_info.split("|")
    account_num = account_info[0]
    account_pin = account_info[1]
    account = get_acct(account_num)

    if (account != False):
        if (account.acct_pin == account_pin):
            client_connection.send(str(1).encode("utf-8"))
            return True
        else:
            client_connection.send(str(2).encode("utf-8"))
            return False
    else:
        client_connection.send(str(3).encode("utf-8"))
        return False


def run_network_server():
    # """ This and all supporting code needs to be written! """


    # print("Bank server network functions not implemented!!")
    # return
   
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

            # Accepting any incoming connections
            client_conn, client_addy = serv_sock.accept()
            print(f"Accepted connection from {client_conn} at {client_addy}.")

            # Sends instructions to the client
            instructions = "You have connected to the ATM Server."
            client_conn.send(instructions.encode("utf-8"))

            while True:
                if (validate_user_info(client_conn)):
                    client_transac = client_conn.recv(1024)
                    client_transac = client_transac.decode("utf-8")

                    # if client_transac == "d":

                    # elif (client_transac == "w"):

                    # elif (client_transac == "x"):
                    
                    # else:

                    break

               
    
            # Closes connection socket with the client
            client_conn.close()
            print("Connection to client has been closed.")
            #Closes server socket
            serv_sock.close()
    except:
        print('Failed to create socket:(')
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