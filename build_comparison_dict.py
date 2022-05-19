import imp
from wordle_common import buildWordList, compare
from tqdm import tqdm


def main():
    comparison_dict = {}
    for answer in tqdm(buildWordList()):
        guess_dict = {}
        for guess in buildWordList():
            guess_dict[guess] = compare(answer, guess)
            
        comparison_dict[answer] = guess_dict
    
    file = open('output.json', 'w')
    file.write(str(comparison_dict))
    file.close()



if __name__ == '__main__':
    main()