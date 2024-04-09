#!/usr/bin/python3

import time
import random
import contextlib

# Create function to time other functions
def tictoc(func):
	def wrapper():
		t1 = time.time()
		func()
		t2 = round(time.time()-t1,4)
		print(f"{func.__name__}() ran in {t2} seconds")
	return wrapper

# Collect user info
def deposit():
	# Keep asking until user provides valid amount
	while True:
		amount = input("What would like to deposit? $")
		if amount.isdigit():
			# Input is returned as string by default so convert to integer
			amount = int(amount)
			if amount > 0:
				break
			else:
				print("Amount must be greater than 0.")
		else:
			print("Please enter a number.")
	return amount

def get_number_of_lines():
	# Keep asking until user provides valid amount
	while True:
		# One way of inserting variables into strings (conversion and concatenation)
		lines = input("Enter the number of lines to bet on (1-" + str(MAX_LINES) + ")? ")
		if lines.isdigit():
			# Input is returned as string by default so convert to integer
			lines = int(lines)
			if 1 <= lines <= MAX_LINES:
				break
			else:
				print("Enter a valid number of lines")
		else:
			print("Please enter a number.")
	return lines

def get_bet():
	# Keep asking until user provides valid amount
	while True:
		amount = input("What would you like to bet on each line? $")
		if amount.isdigit():
			# Input is returned as string by default so convert to integer
			amount = int(amount)
			if MIN_BET <= amount <= MAX_BET:
				break
			else:
				# Different way of inserting variables into strings
				# $ is only there to indicate money, it's not part of the syntax
				print(f"Amount must be between ${MIN_BET} - ${MAX_BET}")
		else:
			print("Please enter a number.")
	return amount

# We will pass 3 parameters to this function
# The parameters don't have to match the actual name of the variables
def spin_slot_machine(rows, cols, symbols):
	# In order to put new symbols in each row and column every time we spin
	# we should create a list and select symbols from it randomly

	# Create empty list and add all possible symbols to it
	# We could create the list statically but by iterating over the dictionary
	# we can dynamically adjust the chances of any given symbol being picked later on if we want
	all_symbols = []
	# Since we're iterating over the dictionary parameter we're passing to this function
	# (which is basically a list of key:value pairs) we can use the items() method
	# which will iterate over both (key=symbol and # of value=# of instances) instead of only one
	for symbol, instance in symbols.items():
		# _ is an anonymous variable
		# Since we don't care about the iteration value (or rather what iteration # we're on) we can use this
		# to keep us from having an unused variable

		# Iterate over values for each key to add corresponding # of instances for each symbol
		for _ in range(instance):
			# Add key (or rather symbol) to list
			all_symbols.append(symbol)
	#print(all_symbols)

	# Randomly select and place symbols in all rows and place those rows in our columns for each spin
	# To visualize it: (reels = [[], [], []])
	reels = []
	# Iterate over number of columns we established in global variable
	for _ in range(cols):
		column = []
		# Create copy of list (as opposed to just a reference to the variable)
		current_symbols = all_symbols[:]
		# Iterate over all rows for given column
		for _ in range(rows):
			# The choice() method returns a randomly selected element
			var = random.choice(current_symbols)
			# Remove it from the list so the probability of choosing the same symbol for the same
			# column decreases correspondingly
			current_symbols.remove(var)
			# Add "row" to column
			column.append(var)
		# Once all rows have been filled, add column to reel
		reels.append(column)
	#print(reels)
	#print(len(reels))
	#return reels

	# Transpose the reel matrix using naive method to display them vertically
	# This method only works up to a certain amount of rows and columns for some reason
	# Take length of list and iterate over it
	# In this case reel has 3 lists (or columns) so i = 3
	# reel[0] assumes there's always at least 1 column, if we passed a parameter with 0 columns
	# it would crash
	for i in range(len(reels[0])):
		for row in reels:
			# Print row
			# Select character in row based on position, print it, and end the line with " | "
			print(row[i], end=" | ")
		# Print empty line so as to print each row in its own line
		print()

def check_winnings(reels, lines, bet, values):
	winnings = 0
	# Iterate over # of lines (rows) player bet on to check if all 3 symbols in a given row match
	# Lines are positional meaning the player doesn't get to choose which rows they bet on, rather
	# they go in order from top to bottom
	# If player only bet on 2, the remaining rows will not be checked because the range will be 0-1
	for line in range(lines):
	# Check what the first symbol in current row is (reels[][]=reels(x,y)=reels(column,row))
		first_symbol = reels[0][lines]
		# Iterate over all columns to compare the other symbols in the row
		# Iterate over objects, not range
		for column in reels:
			# Define what symbol to compare to
			# This basically compares the first symbol with itself during the first run
			symbol_to_check = reels[line]
			# If symbols don't match, player lost that line, so break from for-loop and check next line (row)
			# if symbol does match, continue for-loop and check next column's symbol
			if first_symbol != symbol_to_check:
				break
		# this else is for the for loop
		# if all symbols match, no break occurs and else statement runs for that particular line
		else:
			# This will return the multiplier given the symbol associated with it and multiply it by the bet
			winnings = values[first_symbol] * bet
	return winnings

# Add python decorator to run this function inside tictoc
#@tictoc
def main():
	balance = deposit()
	lines = get_number_of_lines()
	while True:
		bet = get_bet()
		total_bet = lines * bet
		max_dynamic_bet = round(balance / lines)
		if total_bet > balance:
			print(f"${bet} on {lines} lines is ${total_bet}, which exceeds your balance of ${balance}\n"
			      f"Your maximum bet per line is ${max_dynamic_bet}")
		else:
			break
	print(f"You are betting ${bet} on {lines} lines.\nYour total bet is ${total_bet}")
	reels = spin_slot_machine(ROWS,COLS,symbols)
	winnings = check_winnings(reels, lines, bet, values):
#---------------------------------------------------------------------------------------------------------------
# Global constant value that will not change (MUST BE ALL CAPS)
MAX_LINES = 3
MAX_BET = 100
MIN_BET = 1

# Number of symbols per reel (dictionary)
# The symbol will be a string followed by its number of instances based on
# how valuable it is (lower is better)
symbols = {"A":2,"B":4,"C":6,"D":8,}
# Determines multiplier based on how rare symbol is
values = {"A":5,"B":4,"C":3,"D":2,}

# Size of slot machine
ROWS = 3
COLS = 3

main()
