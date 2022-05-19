import sys, getopt
import json
import multiprocessing
import itertools
import string
from tqdm import tqdm
import time

from GuessNode import GuessNode
from wordle_common import compare


def main(argv):
    options = 'hw:au'
    longOptions = ['hard-mode', 'starting-word=', 'all', 'use-answer-list']
    
    startingWord = 'crane'
    hardMode = False
    checkAllStartingWords = False
    useAnswerList = False
    
    try:
        arguments, _ = getopt.getopt(argv, options, longOptions)
        
        for arg, value in arguments:
            if arg in ('-h', '--hard-mode'):
                hardMode = True
            elif arg in ('-w', '--starting-word'):
                startingWord = value
            elif arg in ('-a', '--all'):
                checkAllStartingWords = True
            elif arg in ('-u', '--use-answer-list'):
                useAnswerList = True
    except getopt.error as e:
        print(str(e))
    
    results = []
    
    start = time.time()
    
    remaining = set()
    if useAnswerList:
        remaining = buildAnswerList()
    else:
        remaining = buildWordList()
    
    if checkAllStartingWords:
        """ Check all words """
        pool = multiprocessing.Pool()
        wordList = buildWordList()
        results = list(tqdm(pool.map(canSolve, zip(buildWordList(), itertools.repeat(remaining), itertools.repeat(hardMode))), total=len(wordList)))
    else:
        """ Check single word """
        success, guessNode = canSolve(guess=startingWord, remaining=remaining, hardMode=hardMode)
        results = [(success, guessNode)]
    
    afterExecution = time.time()
    
    print('Execution time: ' + str(afterExecution - start) + 's')

    writeGuessNodeList(results)
    
    end = time.time()
    
    print('Write time: ' + str(end - afterExecution) + 's')
    print('Total time: ' + str(end - start) + 's')


def buildWordList():
    """
    Builds the full list of valid words
    Returns:
        The full list of valid words
    """
    with open('words.txt') as file:
        return set(file.read().splitlines())
    # return set(['trace', 'track', 'brace', 'trick', 'trims', 'brick', 'brims', 'click', 'flick'])


def buildAnswerList():
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


def canSolve(guess: string,
             remaining: set,
             hardMode: bool,
             guesses: set = set(),
             allWords: set = buildWordList()):
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
    
    guessNode = GuessNode(guess)
    comparisonGroups = getComparisonGroups(guess, remaining)
    
    # Ensure the guess reveals information. A guess reveals no information if the guess results in the same comparison pattern for each remaining word
    if len(comparisonGroups) == 1 and 'ggggg' not in comparisonGroups.keys() and len(next(iter(comparisonGroups))) >= len(remaining):
        return False, GuessNode('')
    
    # Loop over each comparison group
    for pattern, words in comparisonGroups.items():
        
        # Set words available to be guessed. Use variable "allWords" for standard mode, and variable "words" for hard mode
        availableWords = set()
        if hardMode:
            availableWords = set(words).difference(guesses)
        else:
            availableWords = allWords.difference(guesses)
        
        if pattern != 'ggggg':
    
            if len(guesses) > 5:
                return False, GuessNode('')
            
            validGuesses = []
            
            # Loop over each word remaining from given comparison pattern and check if it always results in a solved puzzle
            for nextGuess in availableWords:
                success, nextGuessNode = canSolve(guess=nextGuess,
                                                  remaining=words,
                                                  hardMode=hardMode,
                                                  guesses=guesses,
                                                  allWords=allWords)
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
    main(sys.argv[1:])