import sys, getopt
import json
import multiprocessing
import itertools
import string
from tqdm import tqdm
import time

from GuessNode import GuessNode
from wordle_common import fast_compare, ANSWERS, WORDS


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
        remaining = ANSWERS
    else:
        remaining = WORDS
    
    # # -u
    # remaining = ANSWERS
    # # -h
    # hardMode = True
    
    if checkAllStartingWords:
        """ Check all words """
        pool = multiprocessing.Pool()
        wordList = WORDS
        results = list(tqdm(pool.map(canSolve, zip(WORDS, itertools.repeat(remaining), itertools.repeat(hardMode))), total=len(wordList)))
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
    # wordSet = set(remaining)
    
    for answer in remaining:
        comparison = fast_compare(answer, guess)
        
        if comparison not in comparisonGroups.keys():
            comparisonGroups[comparison] = set([answer])
        else:
            comparisonGroups[comparison].add(answer)
    
    # while len(wordSet) > 0:
    #     # pick an arbitrary answer
    #     answer = wordSet.pop()
        
    #     # fast_compare it to the guess (comparison = "gbbyb")
    #     comparison = fast_compare(answer, guess)
        
    #     # get the remaining valid words using the guess and comparison
    #     words = getRemainingWords(remaining, guess, comparison)
        
    #     # set the value of the comparison to be the list of remaining words ("gbbyb": {"windy", ...})
    #     comparisonGroups[comparison] = words
        
    #     # remove those words from the wordSet
    #     wordSet = wordSet.difference(set(words))
        
        
    # print(json.dumps(comparisonGroups, indent=4, sort_keys=True))

    return comparisonGroups


def canSolve(guess: str,
             remaining: set,
             hardMode: bool,
             already_attempted_hard_mode: bool = False,
             guesses: set = set(),
             allWords: set = WORDS):
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
    
    comparison_group_iter = comparisonGroups.items()
    if len(guesses) == 1:
        comparison_group_iter = tqdm(iterable=comparison_group_iter)
    
    # Loop over each comparison group
    for pattern, words in comparison_group_iter:
        
        if pattern != 'ggggg':
    
            if len(guesses) > 5:
                return False, GuessNode('')
        
            # Set words available to be guessed. Use variable "allWords" for standard mode, and variable "words" for hard mode
            available_answers = words.difference(guesses)
            
            validGuesses = []
            
            available_non_answers = set()
            if not already_attempted_hard_mode:
                # Loop over each word remaining from given comparison pattern and check if it always results in a solved puzzle
                for nextGuess in available_answers:
                    success, nextGuessNode = canSolve(guess=nextGuess,
                                                    remaining=words,
                                                    hardMode=True,
                                                    guesses=guesses,
                                                    allWords=allWords)
                    guesses.remove(nextGuess)
                    
                    if success:
                        validGuesses.append(nextGuessNode)
                        guessNode.setNextGuesses(pattern, validGuesses)
                        break
                
                if len(validGuesses) == 0 and not hardMode:
                    available_non_answers = allWords.difference(guesses).difference(available_answers)
                    
                    # Loop over each word remaining from given comparison pattern and check if it always results in a solved puzzle
                    for nextGuess in available_non_answers:
                        success, nextGuessNode = canSolve(guess=nextGuess,
                                                        remaining=words,
                                                        hardMode=True,
                                                        guesses=guesses,
                                                        allWords=allWords)
                        guesses.remove(nextGuess)
                        
                        if success:
                            validGuesses.append(nextGuessNode)
                            guessNode.setNextGuesses(pattern, validGuesses)
                            break
            
            if len(validGuesses) == 0 and not hardMode:
                for nextGuess in available_answers:
                    success, nextGuessNode = canSolve(guess=nextGuess,
                                                    remaining=words,
                                                    hardMode=False,
                                                    already_attempted_hard_mode=not already_attempted_hard_mode,
                                                    guesses=guesses,
                                                    allWords=allWords)
                    guesses.remove(nextGuess)
                    
                    if success:
                        validGuesses.append(nextGuessNode)
                        guessNode.setNextGuesses(pattern, validGuesses)
                        break
            
            if len(validGuesses) == 0 and not hardMode:
                # Loop over each word remaining from given comparison pattern and check if it always results in a solved puzzle
                for nextGuess in available_non_answers:
                    success, nextGuessNode = canSolve(guess=nextGuess,
                                                    remaining=words,
                                                    hardMode=False,
                                                    already_attempted_hard_mode=not already_attempted_hard_mode,
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