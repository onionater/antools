###########################
##      TA SOLUTIONS     ##
###########################
# This document contains  #
# suggested solutions for #
# the problems we propose #
# that use only methods   #
# students will know.     #
###########################


# 1 # GREET #####################################
# Given a name, return the string               #
# 'Hello [name]'                                #
#################################################

def greet( name ):
	return "Hello " + name

# 2 # PIG LATIN #################################
# Given a single word (no surrounding spaces),  #
# return a piglatinized version. We define this #
# as the second letter of the word onwards,     #
# followed by a dash, then the first letter and #
# the string 'ay'                               #
#                                               #
# Examples:                                     #
# * pig_latin('hello') -> 'ello-hay'            #
# * pig_latin('python') -> 'ython-pay'          #
# * pig_latin('MIT') -> 'IT-May'                #
#################################################

def pig_latin( word ):
	return word[1:] + '-' + word[0] + "ay"


# 3 # ELLO-HAY! #################################
# Given a name, say hello to that name's        #
# piglatin equivalent. Designed to demonstrate  #
# the combining functions can provide new       #
# functionality.                                #
#################################################

print greet( pig_latin( 'Luke' ) ) # -> 'Hello uke-Lay'

# 4 # MEET AND GREET ############################
# Demonstrate Lists.                            #
# Be sure to make clear that append and pop can #
# be interspersed with each other.              #
#################################################

movie_line = []

movie_line.append( 'Kojo' )
movie_line.append( 'Joy' )

print greet(movie_line.pop(0)) # -> 'Kojo'

movie_line.append( 'Will' )
movie_line.append( 'Klee' )

print greet(movie_line.pop(0)) # -> 'Joy'
print greet(movie_line.pop(0)) # -> 'Will'

# 5 # UTTING-PAY T-IAY OGETHER-TAY ##############
# Use a list comprehension to piglatinize       #
# Sentences (note that we here define a         #
# sentence as a list of words).                 #
#                                               #
# ** DO NOT USE FOR LOOPS OR WHILE LOOPS **     #
# (unless the student already understands these #
# concepts). Student have not yet been          #
# introduced to these concepts. Instead try to  #
# present list comprehensions as a primitive,   #
# or a way to apply a function across a list.   #
#################################################

def pig_latin_sentence(sentence):
	return [pig_latin(word) for word in sentence]

print pig_latin_sentence(["Hello", "python", "students", "from", "MIT"])
