from array import array
import json


class GuessNode:
    def __init__(self, value, is_json=False):
        if (is_json):
            self.guess = value['guess']
            self.next_guesses = {}
            
            next_guess_json = value['next_guesses']
            for pattern, guess_node_list in next_guess_json.items():
                guess_nodes = []
                for node in guess_node_list:
                    guess_nodes.append(GuessNode(node, True))
                
                self.next_guesses[pattern] = guess_nodes
        else:
            # string
            self.guess = value

            # dict
            # <pattern>: [
            #   GuessNode...
            # ]
            self.next_guesses = {}
    
    def set_next_guesses(self, pattern: str, valid_guesses: list):
        self.next_guesses[pattern] = valid_guesses

    def to_string(self, spaces=0):
        ret = (' ' * spaces) + '{\n'
        ret += (' ' * (spaces + 2)) + '"guess": \"' + self.guess + '\",\n'
        ret += (' ' * (spaces + 2)) + '"next_guesses": {'
        add_pattern_comma = False
        for pattern, valid_guesses in self.next_guesses.items():
            if add_pattern_comma:
                ret += ',\n'
            else:
                ret += '\n'
                add_pattern_comma = True
            ret += (' ' * (spaces + 4)) + '"' + pattern + '": [\n'
            add_list_comma = False
            for guess in valid_guesses:
                if add_list_comma:
                    ret += ',\n'
                else:
                    add_list_comma = True
                ret += guess.to_string(spaces + 6)
            ret += '\n' + (' ' * (spaces + 4)) + ']'
        if add_pattern_comma:
            ret += '\n' + (' ' * (spaces + 2)) + '}\n'
        else:
            ret += '}\n'
        ret += (' ' * spaces) + '}'
        
        return ret