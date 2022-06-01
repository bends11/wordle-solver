import sys
import json
from GuessNode import GuessNode
from wordle_common import compare

def main(argv):
    if len(argv) < 1:
        solve()
    else:
        solve_with_answer(argv[0])

def build_guess_nodes():
    guess_nodes = []
    with open('solution.json') as file:
        json_list = json.loads(file.read())
        for node in json_list:
            guess_nodes.append(GuessNode(node, True))
    
    return guess_nodes

def solve_with_answer(answer):
    guess_node = build_guess_nodes()[0]
    guess = guess_node.guess
    guesses = [guess]
    while guess != answer and len(guesses) < 6:
        comparison = compare(answer, guess)
        guess_node = guess_node.next_guesses[comparison][0]
        guess = guess_node.guess
        guesses.append(guess)
    
    if guess == answer:
        print('Solved in ' + str(len(guesses)) + ' guesses!')
        print(guesses)
    else:
        print('Failed to solve \'' + answer + '\'')

def solve():
    guess_node = build_guess_nodes()[0]
    guess = guess_node.guess
    guesses = [guess]
    print('Enter "' + guess + '" as your next guess')
    comparison = input('Enter the colors returned from your guess (Green: "g", Yellow: "y", Blank: "b"):')
    while comparison != 'ggggg' and len(guesses) < 6:
        guess_node = guess_node.next_guesses[comparison][0]
        guess = guess_node.guess
        guesses.append(guess)
        print('Enter "' + guess + '" as your next guess')
        comparison = input('Enter the colors returned from your guess (Green: "g", Yellow: "y", Blank: "b"):')


if __name__ == '__main__':
    main(sys.argv[1:])