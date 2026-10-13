import re


class Stack:
    """A simple stack implemented using a Python list."""

    def __init__(self):
        self.items = []

    def push(self, item):
        """Add an item to the top of the stack."""
        self.items.append(item)

    def pop(self):
        """Remove and return the top item."""
        if self.is_empty():
            raise ValueError("Cannot pop from an empty stack.")
        return self.items.pop()

    def peek(self):
        """Return the top item without removing it."""
        if self.is_empty():
            raise ValueError("Cannot peek at an empty stack.")
        return self.items[-1]

    def is_empty(self):
        """Check whether the stack is empty."""
        return len(self.items) == 0


def tokenize(expression):
    """Split an expression into numbers and operators."""
    tokens = re.findall(
        r"\d+(?:\.\d+)?|[+\-*/()]|\S",
        expression
    )

    if not tokens:
        raise ValueError("The expression is empty.")

    if "".join(tokens) != re.sub(r"\s+", "", expression):
        raise ValueError("Invalid character in expression.")

    return tokens


def to_postfix(tokens):
    """Convert an infix expression to postfix using a stack."""
    output = []
    operators = Stack()

    precedence = {
        "u+": 3,
        "u-": 3,
        "*": 2,
        "/": 2,
        "+": 1,
        "-": 1
    }

    right_associative = {"u+", "u-"}
    previous = None

    for token in tokens:

        if re.fullmatch(r"\d+(?:\.\d+)?", token):
            if previous in {"number", ")"}:
                raise ValueError("Missing operator.")

            output.append(token)
            previous = "number"

        elif token == "(":
            if previous in {"number", ")"}:
                raise ValueError("Missing operator before '('.")

            operators.push(token)
            previous = "("

        elif token == ")":
            if previous is None or previous in {"operator", "("}:
                raise ValueError("Invalid or empty parentheses.")

            while (
                not operators.is_empty()
                and operators.peek() != "("
            ):
                output.append(operators.pop())

            if operators.is_empty():
                raise ValueError("Mismatched parentheses.")

            operators.pop()
            previous = ")"

        elif token in {"+", "-", "*", "/"}:

            if previous is None or previous in {"operator", "("}:
                if token not in {"+", "-"}:
                    raise ValueError("Invalid operator position.")

                token = "u" + token

            elif previous not in {"number", ")"}:
                raise ValueError("Invalid operator sequence.")

            while (
                not operators.is_empty()
                and operators.peek() != "("
            ):
                top = operators.peek()

                if (
                    precedence[top] > precedence[token]
                    or (
                        precedence[top] == precedence[token]
                        and token not in right_associative
                    )
                ):
                    output.append(operators.pop())
                else:
                    break

            operators.push(token)
            previous = "operator"

        else:
            raise ValueError(f"Invalid token: {token}")

    if previous in {None, "operator", "("}:
        raise ValueError("Incomplete expression.")

    while not operators.is_empty():
        operator = operators.pop()

        if operator == "(":
            raise ValueError("Mismatched parentheses.")

        output.append(operator)

    return output


def evaluate_postfix(tokens):
    """Evaluate a postfix expression using a value stack."""
    values = Stack()

    for token in tokens:

        if re.fullmatch(r"\d+(?:\.\d+)?", token):
            values.push(float(token))

        elif token in {"u+", "u-"}:
            if values.is_empty():
                raise ValueError("Missing operand.")

            number = values.pop()

            if token == "u+":
                values.push(number)
            else:
                values.push(-number)

        else:
            if len(values.items) < 2:
                raise ValueError("Missing operand.")

            right = values.pop()
            left = values.pop()

            if token == "+":
                result = left + right

            elif token == "-":
                result = left - right

            elif token == "*":
                result = left * right

            elif token == "/":
                if right == 0:
                    raise ValueError("Division by zero.")

                result = left / right

            else:
                raise ValueError(f"Unsupported operator: {token}")

            values.push(result)

    if len(values.items) != 1:
        raise ValueError("Invalid expression.")

    return values.pop()


def format_result(value):
    """Format whole numbers without unnecessary decimal places."""
    if value == int(value):
        return str(int(value))

    return f"{value:.10g}"


def evaluate_expression(expression):
    """Tokenize, convert, and evaluate a mathematical expression."""
    tokens = tokenize(expression)
    postfix = to_postfix(tokens)
    result = evaluate_postfix(postfix)

    return format_result(result)


def is_separator(line):
    """Recognise separator lines containing at least three dashes."""
    return bool(re.fullmatch(r"\s*-{3,}\s*", line))


def process_files():
    """Read input.txt and write the evaluated results to output.txt."""
    try:
        with open("input.txt", "r", encoding="utf-8") as source:
            lines = source.readlines()

        output_lines = []

        for line in lines:
            content = line.strip()

            if not content:
                output_lines.append(line.rstrip("\r\n"))

            elif is_separator(content):
                output_lines.append(line.rstrip("\r\n"))

            else:
                try:
                    result = evaluate_expression(content)
                    output_lines.append(result)

                except (ValueError, OverflowError) as error:
                    output_lines.append(f"ERROR: {error}")

        with open("output.txt", "w", encoding="utf-8") as destination:
            destination.write("\n".join(output_lines))

            if lines:
                destination.write("\n")

        print("Processing complete. Results saved to output.txt.")

    except FileNotFoundError:
        print("Error: input.txt was not found in the project folder.")

    except OSError as error:
        print(f"File error: {error}")


if __name__ == "__main__":
    process_files()