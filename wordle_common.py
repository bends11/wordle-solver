


import json
import time


def fast_compare(answer, guess) -> str:
    return __COMPARISONS__[answer][guess]

def compare(answer, guess) -> str:
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
    guess_chars = {}
    answer_chars = {}

    for char in guess:
        if char not in (guess_chars.keys()):
            guess_chars[char] = guess.count(char)
            answer_chars[char] = answer.count(char)

        if answer[index] == char:
            ret.append('g')
            guess_chars[char] -= 1
            answer_chars[char] -= 1
        else:
            ret.append('b')

        index += 1
    
    for char, count in guess_chars.items():
        if count > 0 and answer_chars[char] > 0:
            remaining = min(count, answer_chars[char])
            index = 0
            for g_char in guess:
                if g_char == char and ret[index] == 'b':
                    ret[index] = 'y'
                    remaining -= 1
                    if remaining == 0:
                        break

                index += 1

    return ''.join(ret)

def __build_comparison_dict__():
    try:
        with open('comparisons.json') as file:
            return json.loads(file.read())
    except:
        print('comparisons.json has not been created')

def __build_word_list__():
    """
    Builds the full list of valid words
    Returns:
        The full list of valid words
    """
    with open('words.txt') as file:
        return set(file.read().splitlines())
    # return set(['trace', 'track', 'brace', 'trick', 'trims', 'brick', 'brims', 'click', 'flick'])


def __build_answer_list__():
    """
    Builds the full list of answers
    Returns:
        The full list of answers
    """
    with open('answers.txt') as file:
        return set(file.read().splitlines())
    # return set(['trace', 'track', 'brace', 'trick', 'trims', 'brick', 'brims', 'click', 'flick'])


def get_remaining_words(words, guess, comparison):
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
    matched_locations = {}
    
    # maps an index to a character indicating the answer does NOT have that character at that index
    excluded_locations = {}
    
    # maps a character to the minimum number of times it occurs in the answer
    counts = {}
    
    # the set of characters for which the counts dict has the exact number of occurrences in the answer
    max_reached = set()
    
    index = 0
    for comp in comparison:
        char = guess[index]
        if comp == 'g':
            matched_locations[index] = char
            if char not in (counts.keys()):
                counts[char] = 1
            else:
                counts[char] += 1
        elif comp == 'y':
            excluded_locations[index] = char
            if char not in (counts.keys()):
                counts[char] = 1
            else:
                counts[char] += 1
        else: ## comp == 'b'
            max_reached.add(char)
            excluded_locations[index] = char
            if char not in (counts.keys()):
                counts[char] = 0

        index += 1

    
    ret = set()
    for word in words:
        valid = True
        
        # Ensure the green letters match
        for loc, char in matched_locations.items():
            if word[loc] != char:
                valid = False
                break

        if not valid:
            continue
        
        # Ensure the yellow/black letters don't match
        for loc, char in excluded_locations.items():
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

            if cnt > count and char in max_reached:
                valid = False
                break

        if valid:
            ret.add(word)
    
    return ret


start = time.time()
print('building comparison dict...')
__COMPARISONS__ = __build_comparison_dict__()
end = time.time()
print('comparison dict built in ' + str(end - start) + 's')

WORDS = __build_word_list__()
ANSWERS = __build_answer_list__().intersection(WORDS)
