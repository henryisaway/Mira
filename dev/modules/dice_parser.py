import random

MAX_DICE = 9999
MAX_SIZE = 999

def parseExpression(expression):
    tokens = []
    curToken = []
    curOperator = '+'
    tokenCount = 0

    if expression and expression[0] in '+-':
        curOperator = expression[0]
        tokenCount = 1

    for char in expression[tokenCount:]:
        if char in '+-':
            if curToken:
                tokens.append((curOperator, ''.join(curToken)))
                curToken = []
            curOperator = char
        else:
            curToken.append(char)
    if curToken:
        tokens.append((curOperator, ''.join(curToken)))

    total = 0
    details = []
    for op, token in tokens:
        if not token:
            raise ValueError("Token vazio na expressão")

        if 'd' in token:
            parts = token.split('d')
            if len(parts) != 2:
                raise ValueError(f"Expressão de dado inválida: {token}")
            Xstr, Ystr = parts
            if not Xstr or not Ystr:
                raise ValueError(f"Expressão de dado inválida: {token}")
            try:
                x = int(Xstr)
                y = int(Ystr)
            except ValueError:
                raise ValueError(f"Número de dados inválido: {token}")

            if x > MAX_DICE:
                raise ValueError(f"Limite de dados excedido: {x} (max {MAX_DICE})")
            if y > MAX_SIZE:
                raise ValueError(f"Limite de lados excedido: {y} (max {MAX_SIZE})")

            if x < 1 or y < 1:
                raise ValueError(f"Número de dados inválido: {token}")

            rolls = [random.randint(1, y) for _ in range(x)]
            formattedRolls = [
                f"**{roll}**" if roll == 1 or roll == y else str(roll)
                for roll in rolls
            ]
            sumRolls = sum(rolls)
            details.append(f"{token} ({', '.join(map(str, formattedRolls))})")
            if op == '+':
                total += sumRolls
            else:
                total -= sumRolls
        else:
            try:
                modifier = int(token)
            except ValueError:
                raise ValueError(f"Modificador inválido: {token}")
            details.append(f"{op}{modifier}")
            if op == '+':
                total += modifier
            else:
                total -= modifier

    return total, details