#!/usr/bin/env python3
#
# Automated Teller Machine (ATM) client application.

import socket
import re

##########################################################
#                                                        #
# ATM Client Network Operations                          #
#                                                        #
# NEEDS REVIEW. Changes may be needed in this section.   #
#                                                        #
##########################################################

def send_to_server(sock, msg):
    """ Given an open socket connection (sock) and a string msg, send the string to the server. """
    return sock.send(msg.encode('utf-8'))

def get_from_server(sock):
    """ Attempt to receive a message from the active connection. Block until message is received. """
    msg = sock.recv(1024)
    return msg.decode('utf-8')

def login_to_server(sock, acct_num, pin):
    """ Attempt to login to the bank server. Pass acct_num and pin, get response, parse and check whether login was successful. """
    account_info = "LOG" + " " + str(acct_num) + " " + str(pin) #change thisss.
    send_to_server(sock, account_info)
    validated = (get_from_server(sock))
    return validated

def get_login_info():
    """ Get info from customer. TODO: Validate inputs, ask again if given invalid input. """
    #Validates acct_num to the regex
    while True:
            acct_num_pattern = r"[a-z]{2}-\d{5}"
            acct_num = input("Please enter your account number: ")
            acct_num_match = re.search(acct_num_pattern, acct_num)
            if (acct_num_match):
                break
            else:
                print("Invalid Input. Try Again")
    #Validates pin to the regex
    while True:
        pin_pattern = r"\d{4}"
        pin = input("Please enter your four digit PIN: ")
        pin_num_match = re.search(pin_pattern, pin)
        if (pin_num_match):
           break
        else:
            print("Invalid Input. Try Again")
    return acct_num, pin


def process_deposit(sock):
    """ """
    request_code = "DEP"
    bal = get_acct_balance(sock)
    while True:
        amt = (input(f"How much would you like to deposit? (You have ${bal} available) "))
        msg = request_code + " " + amt
        send_to_server(sock, msg)
        new_bal = get_from_server(sock)
        if (new_bal == "ERR: FORMAT"):
            print("Incorrect format entered.")
            continue
        else:
            print("Deposit transaction completed.")
            print(f"Your balance is: ${round(float(new_bal), 2)}")
            break
    return

def get_acct_balance(sock):
    send_to_server(sock, "BAL")
    bal = get_from_server(sock);
    return bal

def process_withdrawal(sock):
    request_code = "WD"
    bal = get_acct_balance(sock)
    while True:
        amt = (input(f"How much would you like to withdraw? (You have ${bal} available) "))
        msg = request_code + " " + amt
        send_to_server(sock, msg)
        new_bal = get_from_server(sock)
        if (new_bal == "ERR: FORMAT"):
            print("Incorrect format entered.")
            continue
        elif (new_bal == "ERR: OVERDRAFT"):
            print("Insufficient Funds.")
            break
        else: 
            print("Withdrawal transaction completed.")
            print(f"Your balance is: ${round(float(new_bal), 2)}")
            break
    return 

def process_customer_transactions(sock):
    """ Ask customer for a transaction, communicate with server."""
    while True:
        print("Select a transaction. Enter 'd' to deposit, 'w' to withdraw, or 'b' to get balance, or 'x' to exit.")
        req = input("Your choice? ").lower()
        if req not in ('d', 'w', 'x', 'b'):
            print("Unrecognized choice, please try again.")
            continue
        if req == 'x':
            # if customer wants to exit, break out of the loop
            send_to_server(sock, "EXIT")
            break
        elif req == 'd':
            process_deposit(sock)

        elif req == 'b':
            bal = (get_acct_balance(sock))
            print(f"Your balance is: ${round(float(bal), 2)}")
        else:
            process_withdrawal(sock)

def run_atm_core_loop(sock):
    """ Given an active network connection to the bank server, run the core business loop. """
    while True:
        acct_num, pin = get_login_info()
        validated = login_to_server(sock, acct_num, pin)
        if validated == "VALID":
            print("Thank you, your credentials have been validated.")
            process_customer_transactions(sock)
            print("ATM session terminating.")
            return True
        elif validated == "ERR: NO MATCH":
            print("Account number and PIN do not match. Retry login.")
            continue
        elif validated == "ERR: NOT FND":
            print("Account doesn't exist. Retry login.")
            continue
        elif validated == "ERR: NOTRECOG":
            print("Invalid Entry")
            continue

    

##########################################################
#                                                        #
# ATM Client Startup Operations                          #
#                                                        #
# No changes needed in this section.                     #
#                                                        #
##########################################################

def run_network_client():
    """ This function connects the client to the server and runs the main loop. """
    # The bank server's IP address
    HOST = socket.gethostbyname(socket.gethostname())
    # The port used by the bank server
    PORT = 65432   
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            # print(get_from_server(s))
            run_atm_core_loop(s)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    print("Welcome to the ACME ATM Client, where customer satisfaction is our goal!")
    run_network_client()
    print("Thanks for banking with us! Come again soon!!")

    #does say over and over what the account number is. saves the account number once