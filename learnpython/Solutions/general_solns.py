# Some sample people.
alyssa = 19
bob = 21
tom = 13
alice = 5

'''
Given an age, determine if voter is eligible to vote.
'''
def can_vote(age):
    if age >= 18:
        print("You can legally vote!" )
    else:
    	print("You have to wait " + str(18 - age) + " more years :(")
        

'''
Greet every person in a list.
'''
def greet_all(line):
	for person in line:
		print("Hello " + person)

'''
Duplicate the builtin len()
arg:
    some_list
returns:
    How many items are in that list.
'''
def length(some_list):
    count = 0
    for item in some_list:
        count = count + 1
    return count


'''
Given a list of ages, return a list that contains only those
ages that can vote.
'''
def valid_voting_ages( ages ):
    valid = [] # list to contain the answer.
    for age in ages:
        if age >= 18:
            valid.append( age )
        # Otherwise, we don't do anything, just let it pass.
    return valid


can_vote(bob)
can_vote(alice)
print("")
greet_all(['Batman', 'Superman', 'Iron Man'])
print("")
ages = [18, 5, 10, 85, 60, 43, 17]
print(ages)
print(valid_voting_ages(ages))