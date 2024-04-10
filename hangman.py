#!/usr/bin/python3

# This script is a work in progress. I wanted to try my hands at creating a simple hangman game using
# the popular pygame library
# help('pygame')

# Import required libraries
import pygame, sys
# This imports all functions from pygame.locals module
# This syntax is genreally to be more concise about what you're importing
# even thopugh you're still technically importing the whole library
from pygame.locals import *

def main()
	pygame.init()
	DISPLAY = pygame.display.set_mode((500,400),0,32)
	WHITE = (255,255,255)
	BLUE = (0,0,255)
	DISPLAY.fill(WHITE)
	pygame.draw.rect(DISPLAY,BLUE(200,150,100,50))
	while True:
		for event in pygame.event.get():
			if event,type==QUIT:
				pygame.quit()
				sys.exit()
		pygame.display.update()

main()
