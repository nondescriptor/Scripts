#!/usr/bin/python3

# Global constant value that will not change (MUST BE ALL CAPS)
MAX_LINES = 3
MAX_BET = 100
MIN_BET = 1

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

def main():
	balance = deposit()
	lines = get_number_of_lines()
	while True:
		bet = get_bet()
		total_bet = lines * bet
		if total_bet > balance:
			print(f"You cannot bet ${total_bet}.\nYour current balance is: ${balance}")
		else:
			break
	print(f"You are betting ${bet} on {lines} lines.\nYour total bet is equal to: ${total_bet}")

main()
