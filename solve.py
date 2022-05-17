import json
import multiprocessing
import itertools
import string
from tqdm import tqdm
import time

from GuessNode import GuessNode




# def makeGuess(answer, remaining, guess):
#     comparison = compare(answer, guess)
#     return getRemainingWords(remaining, guess, comparison)

# def solve(answer):
#     remaining = buildWordList()
#     numGuesses = 0
#     guess = ''
#     guesses = []
#     while guess != answer and numGuesses < 6:
#         guess = remaining[0]
#         guesses.append(guess)
#         remaining = makeGuess(answer, remaining, guess)
#         numGuesses += 1
    
#     if guess == answer:
#         print('Solved in ' + str(numGuesses) + ' guesses!')
#         print(guesses)
#     else:
#         print('Failed to solve \'' + answer + '\'')

# def findGuess(answer, words, guessNumber):
#     for guess in words:
#         remaining = makeGuess(answer, remaining, guess)
#         if len(remaining) == 1:
#             print('success')
#         elif guessNumber == 5:
#             print('failure')
#         else:
#             findGuess(answer, remaining, guessNumber + 1)
            
            

def buildWordList():
    """
    Builds the full list of valid words
    Returns:
        The full list of valid words
    """
    with open('words.txt') as file:
        return set(file.read().splitlines())
    # return set(['trace', 'track', 'brace', 'trick', 'trims', 'brick', 'brims', 'click', 'flick'])


def compare(answer, guess):
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
    if len(answer) != 5 and len(guess) != 5:
        return []

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

    return ret


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

    
    ret = []
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
            ret.append(word)
    
    return ret


def getComparisonGroups(guess, remaining):
    """
    Gets the dict mapping the comparison pattern ("ggbgg", "yyygb", etc.) to the set of words mathcing that pattern
    
    Example with guess "would"
    {
        "bbbgb": {"apple", ...},
        "bbbyb": {"handy", ...},
        "bbbbb": {"crane", ...},
        "gbbyb": {"windy", ...},
        "gbbbb": {"watch", ...}
    }
    
    Arguments:
        guess: The guess being made
        remaining: The set of words that can still be an answer
    Returns:
        The dict mapping the comparison pattern ("ggbgg", "yyygb", etc.) to the set of words matching that pattern
    """
    comparisonGroups = {}
    wordSet = set(remaining)
    
    while len(wordSet) > 0:
        # pick an arbitrary answer
        answer = wordSet.pop()
        
        # compare it to the guess (comparison = "gbbyb")
        comparison = compare(answer, guess)
        
        # get the remaining valid words using the guess and comparison
        words = getRemainingWords(remaining, guess, comparison)
        
        # set the value of the comparison to be the list of remaining words ("gbbyb": {"windy", ...})
        comparisonGroups[''.join(comparison)] = words
        
        # remove those words from the wordSet
        wordSet = wordSet.difference(set(words))
        
        
    # print(json.dumps(comparisonGroups, indent=4, sort_keys=True))

    return comparisonGroups


def canSolve(guess: string, remaining: set = buildWordList(), guesses: set = set(), allWords: set = buildWordList()):
    """
    Checks if the the given guess will always lead to a solved puzzle
    Arguments:
        guess: The guess being checked
        remaining: The set of words that are still possible solutions
        guesses: The set of guesses alrady made
        allWords: The set of all valid words
    Returns:
        (solveable, guessNode)
        sovleable: True if the guess can be used in a winning strategy for any answer
        guessNode: The GuessNode representing the current guess and all subsequent guesses leading to a solution for every word in the remaining set
    """
    guesses.add(guess)
    
    if len(guesses) > 6:
        return False, GuessNode('')    
    
    guessNode = GuessNode(guess)
    comparisonGroups = getComparisonGroups(guess, remaining)
    
    # Ensure the guess reveals information. A guess reveals no information if the guess results in the same comparison pattern for each remaining word
    if len(comparisonGroups) == 1 and 'ggggg' not in comparisonGroups.keys() and len(next(iter(comparisonGroups))) >= len(remaining):
        return False, GuessNode('')
    
    # Loop over each comparison group
    for pattern, words in comparisonGroups.items():
        
        # Set words available to be guessed. Use variable "allWords" for standard mode, and variable "words" for hard mode
        availableWords = allWords.difference(guesses)
        
        if pattern != 'ggggg':
            validGuesses = []
            
            # Loop over each word remaining from given comparison pattern and check if it always results in a solved puzzle
            for nextGuess in availableWords:
                success, nextGuessNode = canSolve(nextGuess, words, guesses, allWords)
                guesses.remove(nextGuess)
                
                if success:
                    validGuesses.append(nextGuessNode)
                    guessNode.setNextGuesses(pattern, validGuesses)
                    break
            
            # If there are no valid guesses after looping over each remaining word, the given guess does not always result in a solved puzzle
            if len(validGuesses) == 0:
                return False, GuessNode('')

    return True, guessNode


def writeGuessNodeList(results: list):
    """
    Writes a list of results from the canSolve function to output.json
    """
    file = open('output.json', 'w')
    
    file.write('[')

    addComma = False
    for res in results:
        if res[0]:
            if addComma:
                file.write(',\n')
            else:
                file.write('\n')
                addComma = True
            file.write(res[1].toString(2))
    
    if addComma:
        file.write('\n]')
    else:
        file.write(']')
    
    file.close()






if __name__ == '__main__':
    start = time.time()
    
    """ Check single word """
    success, guessNode = canSolve('trace')
    results = [(success, guessNode)]

    """ Check all words """
    # pool = multiprocessing.Pool()
    # wordList = buildWordList()
    # results = list(tqdm(pool.map(canSolve, wordList), total=len(wordList)))
    
    afterExecution = time.time()
    
    print('Execution time: ' + str(afterExecution - start) + 's')

    writeGuessNodeList(results)
    
    end = time.time()
    
    print('Write time: ' + str(end - afterExecution) + 's')
    print('Total time: ' + str(end - start) + 's')