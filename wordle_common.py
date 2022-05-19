


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
    if len(answer) != 5 and len(guess) != 5:
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