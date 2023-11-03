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
    # TODO make sure this works as needed
    return sock.send(msg.encode('utf-8'))

def get_from_server(sock):
    """ Attempt to receive a message from the active connection. Block until message is received. """
    # TODO make sure this works as needed
    msg = sock.recv(1024)
    return msg.decode('utf-8')

def login_to_server(sock, acct_num, pin):
    """ Attempt to login to the bank server. Pass acct_num and pin, get response, parse and check whether login was successful. """
    # TODO: Write this code!
    account_info = str(acct_num) + "|" + str(pin)
    send_to_server(sock, account_info)
    validated = int(get_from_server(sock))
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
  

def process_deposit(sock, acct_num):
    """ TODO: Write this code. """
    bal = get_acct_balance(sock, acct_num)
    while True:
        amt = (input(f"How much would you like to deposit? (You have ${bal} available)"))
        # TODO communicate with the server to request the deposit, check response for success or failure.
        send_to_server(sock, amt)
        new_bal = get_from_server(sock)
        if (new_bal == "010"):
            print("Incorrect format entered.")
            continue
        else:
            print("Deposit transaction completed.")
            print(f"Your balance is: ${new_bal}")
            break
    return

def get_acct_balance(sock, acct_num):
    """ TODO: Ask the server for current account balance. """ #finsihed
    get_from_server(sock)
    send_to_server(sock, acct_num)
    bal = get_from_server(sock);
    return bal

def process_withdrawal(sock, acct_num):
    """ TODO: Write this code. """
     # TODO communicate with the server to request the withdrawal, check response for success or failure.
    bal = get_acct_balance(sock, acct_num)
    while True:
        amt = (input(f"How much would you like to withdraw? (You have ${bal} available) "))
        send_to_server(sock, amt)
        new_bal = get_from_server(sock)
        if (new_bal == "010"):
            print("Incorrect format entered.")
            continue
        elif (new_bal == "012"):
            print("Insufficient Funds.")
            break
        else: 
            print("Withdrawal transaction completed.")
            print(f"Your balance is: ${new_bal}")
            break
    return 

def process_customer_transactions(sock, acct_num):
    """ Ask customer for a transaction, communicate with server. TODO: Revise as needed. """
    while True:
        print("Select a transaction. Enter 'd' to deposit, 'w' to withdraw, or 'b' to get balance, or 'x' to exit.")
        req = input("Your choice? ").lower()
        if req not in ('d', 'w', 'x', 'b'):
            print("Unrecognized choice, please try again.")
            continue
        if req == 'x':
            # if customer wants to exit, break out of the loop
            break
        elif req == 'd':
            send_to_server(sock, "5")
            process_deposit(sock, acct_num)
            # print(f"Your balance is: ${bal}")
        elif req == 'b':
            send_to_server(sock, "6")
            bal = (get_acct_balance(sock, acct_num))
            print(f"Your balance is: ${bal}")
        else:
            send_to_server(sock, "7")
            process_withdrawal(sock, acct_num)
            # print(f"Your balance is: ${bal}")

def run_atm_core_loop(sock):
    """ Given an active network connection to the bank server, run the core business loop. """
    acct_num, pin = get_login_info()
    validated = login_to_server(sock, acct_num, pin)
    if validated == 1:
        print("Thank you, your credentials have been validated.")
        process_customer_transactions(sock, acct_num)
        print("ATM session terminating.")
        return True
    elif validated == 2:
        print("Account number and PIN do not match. Terminating ATM session.")
        return False
    elif validated == 3:
        print("Account doesn't exist. Terminating ATM session.")
        return False

    

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
            print(get_from_server(s))
            run_atm_core_loop(s)
    except Exception as e:
        print(f"Unable to connect to the banking server - exiting...")

if __name__ == "__main__":
    print("Welcome to the ACME ATM Client, where customer satisfaction is our goal!")
    run_network_client()
    print("Thanks for banking with us! Come again soon!!")

    #does say over and over what the account number is. saves the account number once