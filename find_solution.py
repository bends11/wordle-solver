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
    long_options = ['hard-mode', 'starting-word=', 'all', 'use-answer-list']
    
    starting_word = 'crane'
    hard_mode = False
    check_all_starting_words = False
    use_answer_list = False
    
    try:
        arguments, _ = getopt.getopt(argv, options, long_options)
        
        for arg, value in arguments:
            if arg in ('-h', '--hard-mode'):
                hard_mode = True
            elif arg in ('-w', '--starting-word'):
                starting_word = value
            elif arg in ('-a', '--all'):
                check_all_starting_words = True
            elif arg in ('-u', '--use-answer-list'):
                use_answer_list = True
    except getopt.error as e:
        print(str(e))
    
    results = []
    
    start = time.time()
    
    remaining = set()
    if use_answer_list:
        remaining = ANSWERS
    else:
        remaining = WORDS
    
    # # -u
    # remaining = ANSWERS
    # # -h
    # hard_mode = True
    
    if check_all_starting_words:
        """ Check all words """
        pool = multiprocessing.Pool()
        word_list = WORDS
        results = list(tqdm(pool.map(can_solve, zip(WORDS, itertools.repeat(remaining), itertools.repeat(hard_mode))), total=len(word_list)))
    else:
        """ Check single word """
        success, guess_node = can_solve(guess=starting_word, remaining=remaining, hard_mode=hard_mode)
        results = [(success, guess_node)]
    
    after_execution = time.time()
    
    print('Execution time: ' + str(after_execution - start) + 's')

    write_guess_node_list(results)
    
    end = time.time()
    
    print('Write time: ' + str(end - after_execution) + 's')
    print('Total time: ' + str(end - start) + 's')


def get_comparison_groups(guess, remaining):
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
    comparison_groups = {}
    # word_set = set(remaining)
    
    for answer in remaining:
        comparison = fast_compare(answer, guess)
        
        if comparison not in comparison_groups.keys():
            comparison_groups[comparison] = set([answer])
        else:
            comparison_groups[comparison].add(answer)

    return comparison_groups


def can_solve(guess: str,
              remaining: set,
              hard_mode: bool,
              already_attempted_hard_mode: bool = False,
              guesses: set = set(),
              all_words: set = WORDS):
    """
    Checks if the the given guess will always lead to a solved puzzle
    Arguments:
        guess: The guess being checked
        remaining: The set of words that are still possible solutions
        guesses: The set of guesses alrady made
        all_words: The set of all valid words
    Returns:
        (solveable, guess_node)
        sovleable: True if the guess can be used in a winning strategy for any answer
        guess_node: The GuessNode representing the current guess and all subsequent guesses leading to a solution for every word in the remaining set
    """
    guesses.add(guess)
    
    guess_node = GuessNode(guess)
    comparison_groups = get_comparison_groups(guess, remaining)
    
    # Ensure the guess reveals information. A guess reveals no information if the guess results in the same comparison pattern for each remaining word
    if len(comparison_groups) == 1 and 'ggggg' not in comparison_groups.keys() and len(next(iter(comparison_groups))) >= len(remaining):
        return False, GuessNode('')
    
    comparison_group_iter = comparison_groups.items()
    if len(guesses) == 1:
        comparison_group_iter = tqdm(iterable=comparison_group_iter)
    
    # Loop over each comparison group
    for pattern, words in comparison_group_iter:
        
        if pattern != 'ggggg':
    
            if len(guesses) > 5:
                return False, GuessNode('')
        
            # Set words available to be guessed. Use variable "all_words" for standard mode, and variable "words" for hard mode
            available_answers = words.difference(guesses)
            
            valid_guesses = []
            
            available_non_answers = set()
            if not already_attempted_hard_mode:
                # Loop over each word remaining from given comparison pattern and check if it always results in a solved puzzle
                for next_guess in available_answers:
                    success, next_guess_node = can_solve(guess=next_guess,
                                                         remaining=words,
                                                         hard_mode=True,
                                                         guesses=guesses,
                                                         all_words=all_words)
                    guesses.remove(next_guess)
                    
                    if success:
                        valid_guesses.append(next_guess_node)
                        guess_node.set_next_guesses(pattern, valid_guesses)
                        break
                
                if len(valid_guesses) == 0 and not hard_mode:
                    available_non_answers = all_words.difference(guesses).difference(available_answers)
                    
                    # Loop over each word remaining from given comparison pattern and check if it always results in a solved puzzle
                    for next_guess in available_non_answers:
                        success, next_guess_node = can_solve(guess=next_guess,
                                                             remaining=words,
                                                             hard_mode=True,
                                                             guesses=guesses,
                                                             all_words=all_words)
                        guesses.remove(next_guess)
                        
                        if success:
                            valid_guesses.append(next_guess_node)
                            guess_node.set_next_guesses(pattern, valid_guesses)
                            break
            
            if len(valid_guesses) == 0 and not hard_mode:
                for next_guess in available_answers:
                    success, next_guess_node = can_solve(guess=next_guess,
                                                         remaining=words,
                                                         hard_mode=False,
                                                         already_attempted_hard_mode=not already_attempted_hard_mode,
                                                         guesses=guesses,
                                                         all_words=all_words)
                    guesses.remove(next_guess)
                    
                    if success:
                        valid_guesses.append(next_guess_node)
                        guess_node.set_next_guesses(pattern, valid_guesses)
                        break
            
            if len(valid_guesses) == 0 and not hard_mode:
                # Loop over each word remaining from given comparison pattern and check if it always results in a solved puzzle
                for next_guess in available_non_answers:
                    success, next_guess_node = can_solve(guess=next_guess,
                                                         remaining=words,
                                                         hard_mode=False,
                                                         already_attempted_hard_mode=not already_attempted_hard_mode,
                                                         guesses=guesses,
                                                         all_words=all_words)
                    guesses.remove(next_guess)
                    
                    if success:
                        valid_guesses.append(next_guess_node)
                        guess_node.set_next_guesses(pattern, valid_guesses)
                        break
            
            # If there are no valid guesses after looping over each remaining word, the given guess does not always result in a solved puzzle
            if len(valid_guesses) == 0:
                return False, GuessNode('')
                

    return True, guess_node


def write_guess_node_list(results: list):
    """
    Writes a list of results from the canSolve function to output.json
    """
    file = open('output.json', 'w')
    
    file.write('[')

    add_comma = False
    for res in results:
        if res[0]:
            if add_comma:
                file.write(',\n')
            else:
                file.write('\n')
                add_comma = True
            file.write(res[1].to_string(2))
    
    if add_comma:
        file.write('\n]')
    else:
        file.write(']')
    
    file.close()






if __name__ == '__main__':
    main(sys.argv[1:])