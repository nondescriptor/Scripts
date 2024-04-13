#!/bin/python3

# The script asks user how much they want to bet and on how many lines (max 10)
# It creates 3 columns of randomly generated symbols and checks if any row has 3 of a kind
# Finally, it calculates the amount won by the user

class SlotMachine:

	def __init__(self, rows, cols, symbols):
		self.rows = rows
		self.cols = cols
		self.symbols = symbols

	def spin(self):
		# Create list with all possible symbols
		all_symbols = []
		for symbol, instance in self.symbols.items():
			for _ in range(instance):
				all_symbols.append(symbol)

		# Create nested list of rows and columns with symbols picked randomly from list
		reels = []
		for _ in range(self.cols):
			column = []
			current_symbols = all_symbols[:]
			# Number of rows cannot exceed number of symbols in list
			for _ in range(self.rows):
				var = random.choice(current_symbols)
				# Remove it from the list so the probability of choosing the same symbol for the same
				# column decreases correspondingly
				current_symbols.remove(var)
				column.append(var)
			reels.append(column)

		return reels

	# Transpose the reels matrices using naive method to display them vertically
	def transpose(self, reels):
		for i in range(len(reels[0])):
			for column in reels:
				# Select nth element from each column and print it on same row
				print(column[i], end=" | ")
			# Print empty line for next row
			print()

#===============================================================================================================
# Determine user's budget
def deposit():
	while True:
		amount = input("What would like to deposit? $")
		if amount.isdigit():
			amount = int(amount)
			if amount > 0:
				break
			else:
				print("Amount must be greater than 0.")
		else:
			print("Please enter a number.")

	return amount

# Determine how many lines user want to bet on
def get_number_of_lines():
	while True:
		lines = input("Enter the number of lines to bet on (1-"+str(MAX_LINES)+")? ")
		if lines.isdigit():
			lines = int(lines)
			if 1 <= lines <= MAX_LINES:
				break
			else:
				print("Enter a valid number of lines")
		else:
			print("Please enter a number.")

	return lines

# Determine how much user wants to be on each line
def get_bet():
	while True:
		amount = input("What would you like to bet on each line? $")
		if amount.isdigit():
			amount = int(amount)
			if MIN_BET <= amount <= MAX_BET:
				break
			else:
				print(f"Amount must be between ${MIN_BET} - ${MAX_BET}")
		else:
			print("Please enter a number.")

	return amount

# Calculate how much user won
def check_winnings(reels: list, lines: int, bet: int, values: dict) -> int:
	lines_won = 0
	winnings = 0
	# Remove first column because checking it against itself is redundant
	cols_to_check = reels[:]
	var = reels[0]
	cols_to_check.remove(var)
	# Check if all 3 symbols in a given row match
	# Lines are positional meaning the player doesn't get to choose which rows they bet on, rather
	# they go in order from top to bottom
	# If player only bet on 2, any remaining rows will not be checked
	for row in range(lines):
		column_counter = 0
		first_symbol = reels[0][row]
		for column in cols_to_check:
			symbol_to_check = column[row]
			# If symbols don't match, player lost that line, so move to next line
			if first_symbol != symbol_to_check:
				break
			else:
				# If symbols match, check next column
				# Also check if current column is last column
				column_counter += 1
				if len(cols_to_check) != column_counter:
					continue
				else:
					# If no more columns exist then player won line
					winnings += values[first_symbol] * bet
					lines_won += 1

	return winnings, lines_won

# Create function to time other functions
def timer(func):
	def wrapper(*args, **kwargs):
		t1 = time.time()
		result = func(*args, **kwargs)
		t2 = round(time.time()-t1,4)
		print(f"\n\nFunction {func.__name__}() took {t2} seconds")
	return wrapper
#===============================================================================================================
import time # provides time-related functions
import random # generates random numbers
import subprocess, sys # interact with OS

MAX_LINES = 10 # max number of rows player can bet on
MAX_BET = 100
MIN_BET = 1

# Lower number is more valuable
symbols = {"A":2,"B":4,"C":6,"D":8,}
# Define multiplier based on how rare symbol is
values = {"A":5,"B":4,"C":3,"D":2,}

# Size of slot machine
ROWS: int = 10 # Cannot exceed len(all_symbols)
COLS: int = 3 # Can have as many as we want

# Time it just for fun
@timer
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

	# Create slot machine object from class
	machine = SlotMachine(ROWS,COLS,symbols)
	print()

	# Run bash command
	bashCommand = 'read -n 1 -s -r -p "Press any key to spin slot machine...\n"'
	subprocess.run(bashCommand, shell = True, executable="/bin/bash")
	print()

	# Generate reels and print them vertically
	reels = machine.spin()
	reels_vertical = machine.transpose(reels)

	# Calculate winnings
	winnings, lines = check_winnings(reels, lines, bet, values)
	if (winnings > 0) and (lines == 1):
		print(f"\nCongratulations! You won on {lines} line. That's ${winnings}!\n"
			  f"Remaining balance: ${balance - total_bet + prize}")
	elif (winnings > 0) and (lines > 1):
		print(f"\nCongratulations! You won on {lines} lines. That's ${winnings}!\n"
			  f"Remaining balance: ${balance - total_bet + winnings}")
	else:
		print("\nBetter luck next time!")

if __name__ == "__main__":
	main()
