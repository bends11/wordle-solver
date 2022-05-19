import sys
import json
from GuessNode import GuessNode
from wordle_common import compare

def main(argv):
    if len(argv) < 1:
        solve()
    else:
        solveWithAnswer(argv[0])

def buildGuessNodes():
    guessNodes = []
    with open('solution.json') as file:
        jsonList = json.loads(file.read())
        for node in jsonList:
            guessNodes.append(GuessNode(node, True))
    
    return guessNodes

def solveWithAnswer(answer):
    guessNode = buildGuessNodes()[0]
    guess = guessNode.guess
    guesses = [guess]
    while guess != answer and len(guesses) < 6:
        comparison = compare(answer, guess)
        guessNode = guessNode.nextGuesses[comparison][0]
        guess = guessNode.guess
        guesses.append(guess)
    
    if guess == answer:
        print('Solved in ' + str(len(guesses)) + ' guesses!')
        print(guesses)
    else:
        print('Failed to solve \'' + answer + '\'')

def solve():
    guessNode = buildGuessNodes()[0]
    guess = guessNode.guess
    guesses = [guess]
    print('Enter "' + guess + '" as your next guess')
    comparison = input('Enter the colors returned from your guess (Green: "g", Yellow: "y", Blank: "b"):')
    while comparison != 'ggggg' and len(guesses) < 6:
        guessNode = guessNode.nextGuesses[comparison][0]
        guess = guessNode.guess
        guesses.append(guess)
        print('Enter "' + guess + '" as your next guess')
        comparison = input('Enter the colors returned from your guess (Green: "g", Yellow: "y", Blank: "b"):')


if __name__ == '__main__':
    main(sys.argv[1:])