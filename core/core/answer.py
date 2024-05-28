import sympy as sy
import streamlit as st

class SettingViolation(Exception):pass

def calculate_answer(evaluated_question):
    '''
    Takes number, sy.Expr or other valid question. The question should be evaluated, and should not be a str.
    Returns the answer for it.

    The answer will be checked based on the settings, and if there is a fault, RegulationError will be raised.
    '''
    if not isinstance(evaluated_question, sy.Expr):
        # Number problem is already calculated when evaluating
        return evaluated_question

    else:
        # Sympy Expr
        # Answer and settings
        answers = sy.solve(evaluated_question, sy.Symbol('a'))
        settings = st.session_state.settings

        # Complex answers
        if not settings['複素数解を許容する']:
            answers = [ans for ans in answers if ans.has(sy.I)]
            if len(answers) == 0:
                raise SettingViolation('設定違反：虚数解')

        return answers
        
def parse(input:str = None):
    '''
    Parse the recorded user input and returns a latex string.
    return ''.join(st.session_state._input)
    '''
    
    if input is None:
        input = st.session_state.input
    else:
        input = st.session_state[input]
    
    result = " ".join(str(elem) for elem in input)
    result = result.replace("**", "^").replace('*', '').replace('I', 'i')

    return result

def _evaluate(input:str):
    """
    Formats a string into evaluateable form.
    """
    # Default
    if input is None:
        input = st.session_state.input
    else:
        input = st.session_state[input]

    # Check that there is at least one character to evaluate
    if input == []:
        return ""
        
    value_str = ''.join(str(elem) for elem in input).replace('{', '(').replace('}', ')')

    # Check unterminated parenthesis
    if type(input[-1]) == int:
        value_str += ')'

    # Replace the latex log function with a pythonic function styled str
    value_str = re.sub(r'[\\]log_\((\d+?)\)*\((\d+?)\)', r'sy.log(\2, \1)', value_str)
    
    # Replace degree with radian
    value_str = re.sub(r'(\d+)^{[\\]circ}', 'sy.rad(\1)', value_str)
        
    # Replace latex sqrt with math.sqrt function
    value_str = re.sub(r'[\\]sqrt\[2\]\((\d+?)\)', r'sy.sqrt(\1)', value_str)

    # Replace constants
    value_str = value_str.replace(r'\pi', 'sy.pi').replace('I', 'sy.I')

    # Replace calculation signs
    value_str = value_str.replace(r'\times', '*').replace(r'\div', '/').replace('^', '**')

    return value_str

def evaluate(input = None):
    '''
    Raises an error with the streamlit style.
    '''
    value_str = _evaluate(input)

    if value_str == '':
        return ''
        
    try:
         return eval(value_str, 
                    {
                        '__builtins__' : None, 
                        'sy' : sy,
                    },                         
                    {
                        'I' : sy.I # Imaginary
                    } | st.session_state.current_template._characters[0]
                )
        
    except SyntaxError as e:
        st.error(f'無効な式です  \nエラー：Errored string:{value_str}  \nActual error message:{e}')
        return
