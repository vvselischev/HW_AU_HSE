# Given a string, if its length is at least 3,
# add 'ing' to its end.
# Unless it already ends in 'ing', in which case
# add 'ly' instead.
# If the string length is less than 3, leave it unchanged.
# Return the resulting string.
#
# Example input: 'read'
# Example output: 'reading'
def verbing(s):
    len_s = len(s)
    if len_s < 3:
        return s
    if s[len_s - 3:len_s] == "ing":
        s += "ly"
    else:
        s += "ing"
    return s


# Given a string, find the first appearance of the
# substring 'not' and 'bad'. If the 'bad' follows
# the 'not', replace the whole 'not'...'bad' substring
# with 'good'.
# Return the resulting string.
#
# Example input: 'This dinner is not that bad!'
# Example output: 'This dinner is good!'
def not_bad(s):
    not_index = s.find("not")
    bad_index = s.find("bad")
    if 0 <= not_index < bad_index:
            s = s.replace(s[not_index:bad_index + 3], "good")
    return s


# Consider dividing a string into two halves.
# If the length is even, the front and back halves are the same length.
# If the length is odd, we'll say that the extra char goes in the front half.
# e.g. 'abcde', the front half is 'abc', the back half 'de'.
#
# Given 2 strings, a and b, return a string of the form
#  a-front + b-front + a-back + b-back
#
# Example input: 'abcd', 'xy'
# Example output: 'abxcdy'
def front_back(a, b):
    len_front_a = len(a) - len(a) // 2
    len_front_b = len(b) - len(b) // 2
    s = a[:len_front_a] + b[:len_front_b] + a[len_front_a:] + b[len_front_b:]
    return s
