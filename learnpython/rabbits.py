import random
import math
import time

'''
A helper function to print `n` cute ASCII rabbits.
This is a little tricky because each rabbit needs 3 lines to print.
'''
def print_rabbits( n ):
	max_rabbits_in_row = 6  # Feel free to change this number;
				# be forwarned, if it's too big, things
				# will look weird: rabbits will splice.

	# If you're reading through and confused by this next  line,
	# don't worry too much. While loops will be covered a little
	# later; they just repeat until the condition ( i.e. n > 0 )
	# is false, then continue on.
	while n > 0: # While there are still more rabbits to print.
		print '(\___/) ' * min( n, max_rabbits_in_row ) 
		print "(='.'=) " * min( n, max_rabbits_in_row )
		print '(")_(") ' * min( n, max_rabbits_in_row )
		print ''
		n = n - max_rabbits_in_row

'''
Starting with one pair of rabbits, model rabbit reproduction
over a number of months!
http://library.thinkquest.org/27890/theSeries2.html

print a single ascii rabbit ear for every pair of rabbits.
randomize it a little to account for surplus/deficiency of
rabbit friskiness.

Return total number of rabbits at the end.
'''
def model_rabbits(num_months):
    previous = 1
    current = 1
    for i in range(num_months):
        # randomly generate some proportion of rabbits
        # http://docs.python.org/2/library/random.html#random.random
        spread = previous * random.random()

        # round down
        # http://docs.python.org/2/library/math.html#math.trunc
        spread = math.trunc(spread)

        # pick some number of reproducing rabbits
        # http://docs.python.org/2/library/random.html#random.randrange
        pairs_babies = random.randrange(current-spread, current+spread + 1)
        total_pairs = current + pairs_babies

        # str() is casting the integer into a string
        print pairs_babies, 'new pairs of baby rabbits!'
	print ''
        print_rabbits( total_pairs )
        
        # update our values
        previous = current
        current = total_pairs
        time.sleep(1)
    return current

for i in range(1):
    print 'At the end of 5 months, you have', model_rabbits(5), 'rabbits.'
    print "Done. ----------------------------------------------------------------"
