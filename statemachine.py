'''
Basic state machine framework for text parsing
'''

class StateMachine:
    def __init__(self):
        self.handlers = []
        self.startState = None
        self.endStates = []

    def add_state(self, handler, end_state=0):
        # Add states to the state machine by appending a handler
        self.handlers.append(handler)
        if end_state:
            self.endStates.append(handler)

    def set_start(self, handler):
        # Set the starting state
        self.startState = handler

    def run(self, filepath=None):

        handler = self.startState
        # Open a file to read line by line
        with open(filepath,'r') as text:
            while 1:
                # While loop for changing states
                (newState, text) = handler(text)
                if newState in self.endStates:
                    newState(text)
                    break
                elif newState not in self.handlers:
                    print("Invalid target %s", newState)
                else:
                    handler = newState
