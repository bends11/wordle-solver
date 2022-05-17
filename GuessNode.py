from array import array


class GuessNode:
    def __init__(self, guess):
        # string
        self.guess = guess

        # dict
        # <pattern>: [
        #   GuessNode...
        # ]
        self.nextGuesses = {}
    
    def setNextGuesses(self, pattern: str, validGuesses: list):
        self.nextGuesses[pattern] = validGuesses

    def toString(self, spaces=0):
        ret = (' ' * spaces) + '{\n'
        ret += (' ' * (spaces + 2)) + '"guess": \"' + self.guess + '\",\n'
        ret += (' ' * (spaces + 2)) + '"nextGuesses": {'
        addPatternComma = False
        for pattern, validGuesses in self.nextGuesses.items():
            if addPatternComma:
                ret += ',\n'
            else:
                ret += '\n'
                addPatternComma = True
            ret += (' ' * (spaces + 4)) + '"' + pattern + '": [\n'
            addListComma = False
            for guess in validGuesses:
                if addListComma:
                    ret += ',\n'
                else:
                    addListComma = True
                ret += guess.toString(spaces + 6)
            ret += '\n' + (' ' * (spaces + 4)) + ']'
        if addPatternComma:
            ret += '\n' + (' ' * (spaces + 2)) + '}\n'
        else:
            ret += '}\n'
        ret += (' ' * spaces) + '}'
        
        return ret