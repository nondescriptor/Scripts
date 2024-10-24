#!/usr/bin/env python3
# This script encrypts text files in various ways
# run <salt -h> for usage info

import nacl.secret
import nacl.utils
import nacl.pwhash
import base64
import argparse
import subprocess, sys
import getpass
from pathlib import Path

def encrypt_key(input_file):
	# Convert file to bytestring
	with open(input_file, 'r') as plaintext_file:
		contents = plaintext_file.read()
		file = contents.encode("utf-8")

	# Generate random key
	key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
	# Convert it to a string
	key_string = base64.b64encode(key).decode("utf-8")

	# Generate box from key, encrypt file, and check for errors
	box = nacl.secret.SecretBox(key)
	encrypted = box.encrypt(file)
	assert len(encrypted) == len(file) + box.NONCE_SIZE + box.MACBYTES

	# Convert result to a string in order to write it to a file
	encrypted_string = base64.b64encode(encrypted).decode("utf-8")

	return encrypted_string, key_string

def encrypt_passalt(input_file, input_password):
	# Convert file to bytestring
	with open(input_file, 'r') as plaintext_file:
		contents = plaintext_file.read()
		file = contents.encode("utf-8")

	# Generate random salt
	salt_size = nacl.pwhash.argon2i.SALTBYTES
	salt = nacl.utils.random(salt_size)
	# Convert it to a string
	salt_string = base64.b64encode(salt).decode("utf-8")

	# Convert password to bytestring
	password = input_password.encode("utf-8")

	# Define key derivation function
	kdf = nacl.pwhash.argon2i.kdf

	# Generate key from password and salt
	key = kdf(nacl.secret.SecretBox.KEY_SIZE, password, salt)

	# Generate box from key, encrypt file, and check for errors
	box = nacl.secret.SecretBox(key)
	encrypted = box.encrypt(file)
	assert len(encrypted) == len(file) + box.NONCE_SIZE + box.MACBYTES

	# Convert result to a string in order to write it to a file
	encrypted_string = base64.b64encode(encrypted).decode("utf-8")

	return encrypted_string, salt_string

def encrypt_pass(input_file, input_password):
	# Convert file to bytestring
	with open(input_file, 'r') as plaintext_file:
		contents = plaintext_file.read()
		file = contents.encode("utf-8")

	# Convert password to ascii decimal array
	password = list(input_password.encode("ascii"))

	# Generate key from password
	if len(password) > 32:
		print("Password must be less than 32 characters")
		exit()
	elif len(password) < 32:
		# Create array of fixed size corresponding to the number of remaining bytes and merge it with
		# password array
		remainder = 32 - len(password)
		var = [0] * remainder
		key_list = password + var
		# Convert array back to bytestring
		key = ''.join(chr(i) for i in key_list).encode("ascii")
	else:
		# If it's equal to 32 bytes then just copy array
		key_list = password[:]
		# Convert array back to bytestring
		key = ''.join(chr(i) for i in key_list).encode("ascii")

	# Generate box from key, encrypt file, and check for errors
	box = nacl.secret.SecretBox(key)
	encrypted = box.encrypt(file)
	assert len(encrypted) == len(file) + box.NONCE_SIZE + box.MACBYTES

	# Convert result to a string in order to write it to a file
	encrypted_string = base64.b64encode(encrypted).decode("utf-8")

	return encrypted_string

def decrypt_key(input_file, input_key):
	# Convert file to bytestring
	with open(input_file, 'r') as file_encrypted:
		contents = file_encrypted.read()
		file = base64.b64decode(contents)

	# Convert key to bytestring
	key = base64.b64decode(input_key)

	# Generate box from key, decrypt file, and convert result to string
	box = nacl.secret.SecretBox(key)
	decrypted = box.decrypt(file)
	decrypted_string = decrypted.decode("utf-8")

	return decrypted_string

def decrypt_passalt(input_file, input_password, input_salt):
	# Convert file to bytestring
	with open(input_file, 'r') as file_encrypted:
		contents = file_encrypted.read()
		file = base64.b64decode(contents)

	# Convert password to bytestring
	password = input_password.encode("utf-8")

	# Convert salt to bytestring
	salt = base64.b64decode(input_salt)

	# Generate key from password and salt
	kdf = nacl.pwhash.argon2i.kdf
	key = kdf(nacl.secret.SecretBox.KEY_SIZE, password, salt)

	# Generate box from key, decrypt file, and convert result to string
	box = nacl.secret.SecretBox(key)
	decrypted = box.decrypt(file)
	decrypted_string = decrypted.decode("utf-8")

	return decrypted_string

def decrypt_pass(input_file, input_password):
	# Convert file to bytestring
	with open(input_file, 'r') as file_encrypted:
		contents = file_encrypted.read()
		file = base64.b64decode(contents)

	# Convert password to ascii decimal array
	password = list(input_password.encode("ascii"))

	# Generate key from password
	if len(password) > 32:
		print("Password must be less than 32 characters")
		exit()
	elif len(password) < 32:
		# Create array of fixed size corresponding to the number of remaining bytes and merge it with
		# password array
		remainder = 32 - len(password)
		var = [0] * remainder
		key_list = password + var
		# Convert array back to bytestring
		key = ''.join(chr(i) for i in key_list).encode("ascii")
	else:
		# If it's equal to 32 bytes then just copy array
		key_list = password[:]
		# Convert array back to bytestring
		key = ''.join(chr(i) for i in key_list).encode("ascii")

	# Generate box from key, decrypt file, and convert result to string
	box = nacl.secret.SecretBox(key)
	decrypted = box.decrypt(file)
	decrypted_string = decrypted.decode("utf-8")

	return decrypted_string

def main():
	# Use argparse to add flags to script
	# Create parser container for argument specifications
	parser = argparse.ArgumentParser(
		prog="salt",
		usage="salt [-h] or [-ek] [-eps] [-ep] [-dk] [-dps] [-dp] FILENAME",
		description="Program designed to encrypt text files one at a time")

	# Attach individual argument specifications to the parser
	parser.add_argument("-ek", "--encrypt_key", metavar="", help="Encrypt with random key")
	parser.add_argument("-eps", "--encrypt_passalt", metavar="", help="Encrypt with password and salt")
	parser.add_argument("-ep", "--encrypt_pass", metavar="", help="Encrypt with password")
	parser.add_argument("-dk", "--decrypt_key", metavar="", help="Decrypt with key")
	parser.add_argument("-dps", "--decrypt_passalt", metavar="", help="Decrypt with password and salt")
	parser.add_argument("-dp", "--decrypt_pass", metavar="", help="Decrypt with password")

	# Run the parser and place extracted data in argparse.Namespace object
	args = parser.parse_args()

	# Encrypt with key
	if args.encrypt_key:
		input_file = args.encrypt_key
		encrypted, key = encrypt_key(input_file)

		# Overwrite plaintext file
		with open(input_file, 'w') as new:
			new.write(encrypted)

		print(f"\nYour file has been encrypted and your key is:\n\n{key}\n")

	# Encrypt with password and salt
	elif args.encrypt_passalt:
		input_file = args.encrypt_passalt
		input_password = getpass.getpass("\nPassword: ")
		encrypted, salt = encrypt_passalt(input_file, input_password)

		# Overwrite plaintext file
		with open(input_file, 'w') as new:
			new.write(encrypted)

		print(f"\nYour file has been encrypted and your salt is:\n\n{salt}\n")

	# Encrypt with password
	elif args.encrypt_pass:
		input_file = args.encrypt_pass
		input_password = getpass.getpass("\nPassword: ")
		encrypted = encrypt_pass(input_file, input_password)

		# Overwrite plaintext file
		with open(input_file, 'w') as new:
			new.write(encrypted)

		print(f"\nYour file has been encrypted.\n")

	# Decrypt with key
	elif args.decrypt_key:
		input_file = args.decrypt_key
		input_key = getpass.getpass("\nKey: ")
		decrypted = decrypt_key(input_file, input_key)

		# Overwrite encrypted file
		with open(input_file, 'w') as new:
			new.write(decrypted)

		print("\nYour file has been decrypted.\n")

	# Decrypt with password and salt
	elif args.decrypt_passalt:
		input_file = args.decrypt_passalt
		input_password = getpass.getpass("\nPassword: ")
		input_salt = getpass.getpass("\nSalt: ")
		decrypted = decrypt_passalt(input_file, input_password, input_salt)

		# Overwrite encrypted file
		with open(input_file, 'w') as new:
			new.write(decrypted)

		print("\nYour file has been decrypted.\n")

	# Decrypt with password
	elif args.decrypt_pass:
		input_file = args.decrypt_pass
		input_password = getpass.getpass("\nPassword: ")
		decrypted = decrypt_pass(input_file, input_password)

		# Overwrite encrypted file
		with open(input_file, 'w') as new:
			new.write(decrypted)

		print("\nYour file has been decrypted.\n")

	else:
		print("No parameters specified")
		exit()

if __name__ == "__main__":
	main()
