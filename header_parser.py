'''
Parses Tolstoy's War and Peace into header, body, and footer for processing
using a state machine framework.
'''

from statemachine import StateMachine
import sys

# Machine States
def error(text):
    # Catch errors: unidentifiable line
    sys.stderr.write('Unidentifiable line:\n'+ line)

def end(text):
    # End of text
    sys.stdout.write('Processing Successful\n')

def header(text):
    # Start with the header and determine state transition
    # with 10 consecutive blank lines
    fp = text
    blankline_count = 0
    while 1:
        line = fp.readline()
        #print(line)
        if line in ['\n', '\r\n']:  blankline_count += 1
        else:                       blankline_count = 0
        if blankline_count == 10:   return body, fp
        else:                       continue

def body(text):
    # Body state (transition is same as header)
    fp = text
    blankline_count = 0
    body_text = ''
    while 1:
        line = fp.readline()
        body_text += line
        if line in ['\n', '\r\n']:  blankline_count += 1
        else:                       blankline_count = 0
        # Write body text into file for later processing
        if blankline_count == 10:
            with open('warandpeace_body.txt','w') as body_file:
                body_file.write(body_text)
            return footer, fp
        else:                       continue

def footer(text):
    # Footer state, the only transition is end of book
    fp = text
    while 1:
        line = fp.readline()
        print(line)
        if not line:                return end, fp

if __name__== "__main__":
    m = StateMachine()
    m.add_state(header)
    m.add_state(body)
    m.add_state(footer)
    m.add_state(error, end_state=1)
    m.add_state(end, end_state=1)
    m.set_start(header)
    m.run('warandpeace.txt')
