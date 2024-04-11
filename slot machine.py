#!/usr/bin/python3

# This was my first python script so it's a bit verbose with comments
# The script asks user how much they want to bet on how many lines
# It creates 3 columns of randomly generated symbols and checks if any row has 3 of a kind
# Finally, it calculates the amount won by the user

class SlotMachine:

	def __init__(self, rows, cols, symbols):
		self.rows = rows
		self.cols = cols
		self.symbols = symbols

	# The parameters don't have to match the actual name of the variables
	def spin(self):
		# In order to put new symbols in each row and column every time we spin
		# we should create a list and select symbols from it randomly

		# Create empty list and add all possible symbols to it
		# We could create the list statically but by iterating over the dictionary
		# we can dynamically adjust the chances of any given symbol being picked later on if we want
		all_symbols = []
		# Since we're iterating over the dictionary parameter we're passing to this function
		# (which is basically a list of key:value pairs) we can use the items() method
		# which will iterate over both (key=symbol and # of value=# of instances) instead of only one
		for symbol, instance in self.symbols.items():
			# _ is an anonymous variable
			# Since we don't care about the iteration value,
			# or rather what iteration # we're on, we can use this
			# to keep us from having an unused variable

			# Iterate over values for each key to add corresponding # of instances for each symbol
			for _ in range(instance):
				# Add key (or rather symbol) to list
				all_symbols.append(symbol)

		# Randomly select and place symbols in all rows and place those rows in our columns for each spin
		# To visualize it: (reels = [[row1,row2,row3], [row1,row2,row3], [row1,row2,row3]])
		reels = []
		# Iterate over number of columns we established in global variable
		for _ in range(self.cols):
			column = []
			# Create copy of list (as opposed to just a reference to the variable)
			current_symbols = all_symbols[:]
			# Iterate over all rows for given column
			# Number of rows cannot exceed number of symbols
			for _ in range(self.rows):
				# The choice() method returns a randomly selected element
				var = random.choice(current_symbols)
				# Remove it from the list so the probability of choosing the same symbol for the same
				# column decreases correspondingly
				current_symbols.remove(var)
				# Add "row" to column
				column.append(var)
			# Once all rows have been filled, add column to reel
			reels.append(column)
		return reels

	# When defining a function you can make optional parameters
	# If no argument is passed to the function, it will print "hello world" by default
	# Without the equals sign, the parameter is required and positional
	"""
	def hello(user_defined_default_arg="world")
		print("hello,", user_defined__default_arg)
	
	hello()
	name = input("What's your name? ")
	hello(name)
	"""

	def transpose(self, reels):
		# Transpose the reels matrices using naive method to display them vertically
		# Since this is a nested list we will need 2 for-loops

		# Basically print 1st character of each sublist (column) in the same line
		# then print new line for the 2nd and so on
		# For a slot machine with 3 rows and columns
		# column1[0], column2[0], column3[0]
		# column1[1], column2[1], column3[1]
		# column1[2], column2[2], column3[2]

		# Get number of elements in a sublist (column) to iterate over (determines # of rows)
		for i in range(len(reels[0])):
			# Iterate over each sublist (column)
			for column in reels:
				# Select element in column positionally, print it, and add " | " at the end
				# by changing the default value of the parameter
				print(column[i], end=" | ")
			# Once nth element in all sublists has been printed on same line, print new empty line for next row
			print()

#===============================================================================================================
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
	# Return function sends objects/values back to the caller
	# Without return, the output of desposit() will be a None value
	# and any fuction that calls deposit() will receive None as the value
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

# I've applied 'type hints' to this function just for the sake of trying it out
# -> tells us the data type of the output
# Type hints are only really useful when using a static type checker in vscode (or whatever IDE)
# and also to be extra explicit to whoever else comes across your script
def check_winnings(reels: list, lines: int, bet: int, values: dict) -> int:
	winnings = 0
	# Remove first sublist because checking if the 1st symbol matches the first symbol is redundant
	cols_to_check = reels[:]
	var = reels[0]
	cols_to_check.remove(var)
	# Iterate over # of lines (rows) player bet on to check if all 3 symbols in a given row match
	# Lines are positional meaning the player doesn't get to choose which rows they bet on, rather
	# they go in order from top to bottom
	# If player only bet on 2, any remaining rows will not be checked
	for line in range(lines):
		# Check what the first symbol is in each row (all symbols in 1st column)
		# reels[column][row or element #]
		# It helps to visualize it by not thinking about the transposed version
		first_symbol = reels[0][line]
		print(f"first symbol: {first_symbol}")
		# Iterate over all columns, except the first, to compare the other symbols in the current the row
		# does reels[0][0] == reels[1][0]?
		for column in cols_to_check:
			print(column)
			for element in range(lines):
				symbol_to_check = column[element]
				print(symbol_to_check)
				# If symbols don't match, player lost that line, so break out of both for-loops
				# to get new first symbol for next line (row)
				# for-loops will not start over but instead pick up where they left off
				# if symbol does match, continue current for-loop
				# Once last symbol matches, for loop ends and calculate winnings for that row
				if first_symbol != symbol_to_check:
					break
			break
		# this else is for the for loop
		# if all symbols match, no break occurs and else statement runs for that particular line
		#else:
		# Retrieve multiplier given the symbol associated with it
		#winnings = values[first_symbol] * bet
	#return winnings"""

# Create function to time other functions
def timer(func):
	# This wrapper (inner function) is necessary so that the function decorator (timer)
	# receives a function object to decorate, and returns the decorated function
	# Wrapper function will take any positional arguments and any keyword arguments
	# That way, we can pass any function to it
	def wrapper(*args, **kwargs):
		t1 = time.time() # start time
		result = func(*args, **kwargs) # call decorated function
		t2 = round(time.time()-t1,4) # end time
		print(f"\n\nFunction {func.__name__}() took {t2} seconds")
		# We return the result so that the decorated function will always function as if it hadn't been 
		# decorated in the first place (just with additional functionality from the wrapper function)
		#return result
	return wrapper
#===============================================================================================================
# Import required libraries
import time, random, contextlib

# Global constant value that will not change (MUST BE ALL CAPS)
MAX_LINES = 3 # max number of rows player can bet on
MAX_BET = 100
MIN_BET = 1

# Number of symbols per column (dictionary)
# The symbol will be a string followed by its number of instances based on
# how valuable it is (lower is better)
symbols = {"A":2,"B":4,"C":6,"D":8,}
# Determines multiplier based on how rare symbol is
values = {"A":5,"B":4,"C":3,"D":2,}

# Size of slot machine
# I've used type hints here for the sake of trying it out
# Only really useful when used in conjunction with a static type checker
ROWS: int = 3 # Cannot exceed print(len(all_symbols)) (number of all symbols available)
COLS: int = 3 # Can have as many as we want

# Add python decorator to pass this function to timer()
#@timer
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
	# Create slow machine object from class
	machine = SlotMachine(ROWS,COLS,symbols)
	var = input("Would you like to spin the slot machine? ")
	if var == 'yes':
		reels = machine.spin() # Generate reels
		print(reels)
		reels_vertical = machine.transpose(reels) # Print them vertically
	else:
		print("See ya next time!")
		exit()
	winnings = check_winnings(reels, lines, bet, values)
	
	#if winnings > 0:
		#print(f"Congratulations! You've won ${winnings}")

# This convention is importtant to have when importing modules so you don't run code you didn't intend to
# In other words, the code below this line will only execute when run within this script
# and not when imported to other scripts as a module
# Also, in vscode, it helps in ensuring you're running the correct script when switching between tabs
# by running  it from the green arrow next to it instead of clicking run at the top
# It also tells the reader that the script is meant to be run and not just imported
if __name__ == "__main__":
	main()
