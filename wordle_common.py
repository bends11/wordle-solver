


import json


def fast_compare(answer, guess) -> str:
    return __COMPARISONS__[answer][guess]

def __compare__(answer, guess) -> str:
    """
    Compare a guess to an answer and get the comparison pattern.
    
    "b": Black; i.e. this character does not exist at this position and the number of this character in the answer has been exceeded
    "y": Yellow; i.e. this character does not exist at this potision, but the number of this character in the answer has not been exceeded
    "g": Green; i.e. this character exists at this position in the answer
    
    Arguments:
        answer: The answer to the puzzle
        guess: The guess being made
    Returns:
        The comparison pattern (e.g. ["b", "b", "y", "g", "y"])
    """
    if len(answer) != 5 or len(guess) != 5:
        return ''

    ret = []
    index = 0
    guessChars = {}
    answerChars = {}

    for char in guess:
        if char not in (guessChars.keys()):
            guessChars[char] = guess.count(char)
            answerChars[char] = answer.count(char)

        if answer[index] == char:
            ret.append('g')
            guessChars[char] -= 1
            answerChars[char] -= 1
        else:
            ret.append('b')

        index += 1
    
    for char, count in guessChars.items():
        if count > 0 and answerChars[char] > 0:
            remaining = min(count, answerChars[char])
            index = 0
            for gChar in guess:
                if gChar == char and ret[index] == 'b':
                    ret[index] = 'y'
                    remaining -= 1
                    if remaining == 0:
                        break

                index += 1

    return ''.join(ret)

def __buildComparisonDict__():
    with open('comparisons.json') as file:
        return json.loads(file.read())

def __buildWordList__():
    """
    Builds the full list of valid words
    Returns:
        The full list of valid words
    """
    with open('words.txt') as file:
        return set(file.read().splitlines())
    # return set(['trace', 'track', 'brace', 'trick', 'trims', 'brick', 'brims', 'click', 'flick'])


def __buildAnswerList__():
    """
    Builds the full list of answers
    Returns:
        The full list of answers
    """
    with open('answers.txt') as file:
        return set(file.read().splitlines())
    # return set(['trace', 'track', 'brace', 'trick', 'trims', 'brick', 'brims', 'click', 'flick'])


def getRemainingWords(words, guess, comparison):
    """
    Gets the list of remaining words given the guess and comparison pattern

    Arguments:
        words: The possible solutions prior to the guess being made
        guess: The guess being made
        comparison: The pattern resulting from making the guess
    Returns:
        All possible solutions after making the guess
    """
    # maps an index to a character indicating the answer has that character at that index
    matchedLocations = {}
    
    # maps an index to a character indicating the answer does NOT have that character at that index
    excludedLocations = {}
    
    # maps a character to the minimum number of times it occurs in the answer
    counts = {}
    
    # the set of characters for which the counts dict has the exact number of occurrences in the answer
    maxReached = set()
    
    index = 0
    for comp in comparison:
        char = guess[index]
        if comp == 'g':
            matchedLocations[index] = char
            if char not in (counts.keys()):
                counts[char] = 1
            else:
                counts[char] += 1
        elif comp == 'y':
            excludedLocations[index] = char
            if char not in (counts.keys()):
                counts[char] = 1
            else:
                counts[char] += 1
        else: ## comp == 'b'
            maxReached.add(char)
            excludedLocations[index] = char
            if char not in (counts.keys()):
                counts[char] = 0

        index += 1

    
    ret = set()
    for word in words:
        valid = True
        
        # Ensure the green letters match
        for loc, char in matchedLocations.items():
            if word[loc] != char:
                valid = False
                break

        if not valid:
            continue
        
        # Ensure the yellow/black letters don't match
        for loc, char in excludedLocations.items():
            if word[loc] == char:
                valid = False
                break

        if not valid:
            continue

        # Ensure the number of letters is correct for each character
        for char, count in counts.items():
            cnt = word.count(char)
            if cnt < count:
                valid = False
                break

            if cnt > count and char in maxReached:
                valid = False
                break

        if valid:
            ret.add(word)
    
    return ret


__COMPARISONS__ = __buildComparisonDict__()

WORDS = __buildWordList__()
ANSWERS = __buildAnswerList__()