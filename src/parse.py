# Jeremy Ng 500882192
# CPS842 Project

# Function to parse input. **Hard to differentiate "-" between minus or hyphen**
def parse(text):
    chars = ["'s", "'", "-", ".",
             "(", ")", "{", "}", "[", "]", ":", ";", ",", '"', "*", "/", "?", "!", "$", "`"]
    for char in chars:
        if char in text:
            text = text.replace(char, " ")
    operators = {
        "<=": " less than or equal to ",
        ">=": " greater than or equal to ",
        "=": " equal to ",
        "<": " less than ",
        ">": " greater than ",
        "+": " add ",
        "^": " raised to the power of ",
        "&": " and ",
        "%": " percent ",
        "+": " plus "
    }
    for key, val in operators.items():
        if key in text:
            text = text.replace(key, val)
    return text.split()
