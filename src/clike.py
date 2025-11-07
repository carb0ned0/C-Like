import argparse
import sys
from enum import Enum
import os  # Add this for file path handling

_SHOULD_LOG_SCOPE = False  # see '--scope' command line option
_SHOULD_LOG_STACK = False  # see '--stack' command line option
_SHOULD_LOG_DEBUG = False  # see '--debug' command line option


class ErrorCode(Enum):
    UNEXPECTED_TOKEN = 'Unexpected token'
    ID_NOT_FOUND = 'Identifier not found'
    DUPLICATE_ID = 'Duplicate id found'
    ARG_COUNT_MISMATCH = 'Argument count mismatch'
    FILE_NOT_FOUND = 'File not found'  # New error code for import issues


class Error(Exception):
    def __init__(self, error_code=None, token=None, message=None):
        self.error_code = error_code
        self.token = token
        self.message = f'{self.__class__.__name__}: {message}'


class LexerError(Error):
    pass


class ParserError(Error):
    pass


class SemanticError(Error):
    pass


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


###############################################################################
#  LEXER                                                                      #
###############################################################################


class TokenType(Enum):
    # Operators and symbols
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    DIV = '/'  # treat as float division
    ASSIGN = '='
    EQ = '=='
    SEMI = ';'
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'
    NE = '!='
    LT = '<'
    GT = '>'
    LE = '<='
    GE = '>='
    LBRACKET = '['
    RBRACKET = ']'
    COMMA = ','
    AND = '&&'
    OR = '||'
    HASH = '#'  # New for directives like #include

    # Keywords
    WHILE = 'WHILE'
    FOR = 'FOR'
    INT = 'int'
    FLOAT = 'float'
    MAIN = 'main'
    IF = 'if'
    ELSE = 'else'
    VOID = 'void'
    RETURN = 'return'
    INCLUDE = 'include'  # New keyword for #include

    # Misc
    CHAR = 'char'
    STRING = 'string'
    STRING_LITERAL = 'STRING_LITERAL'
    CHAR_LITERAL = 'CHAR_LITERAL'
    PRINT = 'PRINT'
    ID = 'ID'
    INTEGER_CONST = 'INTEGER_CONST'
    FLOAT_CONST = 'FLOAT_CONST'
    EOF = 'EOF'



class Token:
    def __init__(self, type, value, lineno=None, column=None):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.column = column

    def __str__(self):
        return 'Token({type}, {value}, position={lineno}:{column})'.format(
            type=self.type,
            value=repr(self.value),
            lineno=self.lineno,
            column=self.column,
        )

    def __repr__(self):
        return self.__str__()


def _build_reserved_keywords():
    return {
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'int': TokenType.INT,
        'float': TokenType.FLOAT,
        'main': TokenType.MAIN,
        'print': TokenType.PRINT,
        'char': TokenType.CHAR,
        'string': TokenType.STRING,
        'void': TokenType.VOID,
        'return': TokenType.RETURN,
        'include': TokenType.INCLUDE,  # Add 'include' as a keyword
    }


RESERVED_KEYWORDS = _build_reserved_keywords()


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        self.lineno = 1
        self.column = 1

    def error(self):
        s = "Lexer error on '{lexeme}' line: {lineno} column: {column}".format(
            lexeme=self.current_char,
            lineno=self.lineno,
            column=self.column,
        )
        raise LexerError(message=s)

    def advance(self):
        if self.current_char == '\n':
            self.lineno += 1
            self.column = 0

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            self.column += 1

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        token = Token(type=None, value=None, lineno=self.lineno, column=self.column)

        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

        if '.' in result:
            token.type = TokenType.FLOAT_CONST
            token.value = float(result)
        else:
            token.type = TokenType.INTEGER_CONST
            token.value = int(result)

        return token

    def _id(self):
        token = Token(type=None, value=None, lineno=self.lineno, column=self.column)

        value = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            value += self.current_char
            self.advance()

        token_type = RESERVED_KEYWORDS.get(value.lower())
        if token_type is None:
            token.type = TokenType.ID
            token.value = value
        else:
            token.type = token_type
            token.value = value.lower()

        return token

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/' and self.peek() == '/':
                self.advance()
                self.advance()
                while self.current_char is not None and self.current_char != '\n':
                    self.advance()
                continue

            if self.current_char.isalpha() or self.current_char == '_':
                return self._id()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == '=' and self.peek() == '=':
                tok = Token(TokenType.EQ, '==', self.lineno, self.column)
                self.advance(); self.advance()
                return tok

            if self.current_char == '=':
                tok = Token(TokenType.ASSIGN, '=', self.lineno, self.column)
                self.advance()
                return tok

            if self.current_char == '{':
                tok = Token(TokenType.LBRACE, '{', self.lineno, self.column)
                self.advance()
                return tok

            if self.current_char == '}':
                tok = Token(TokenType.RBRACE, '}', self.lineno, self.column)
                self.advance()
                return tok

            if self.current_char == '!' and self.peek() == '=':
                self.advance(); self.advance()
                return Token(TokenType.NE, '!=', self.lineno, self.column)

            if self.current_char == '<' and self.peek() == '=':
                self.advance(); self.advance()
                return Token(TokenType.LE, '<=', self.lineno, self.column)

            if self.current_char == '>' and self.peek() == '=':
                self.advance(); self.advance()
                return Token(TokenType.GE, '>=', self.lineno, self.column)

            if self.current_char == '<':
                self.advance()
                return Token(TokenType.LT, '<', self.lineno, self.column)

            if self.current_char == '>':
                self.advance()
                return Token(TokenType.GT, '>', self.lineno, self.column)

            if self.current_char == '&' and self.peek() == '&':
                self.advance(); self.advance()
                return Token(TokenType.AND, '&&', self.lineno, self.column)

            if self.current_char == '|' and self.peek() == '|':
                self.advance(); self.advance()
                return Token(TokenType.OR, '||', self.lineno, self.column)
            
            if self.current_char == '"':
                self.advance()
                start_col = self.column
                result = ''
                while self.current_char is not None and self.current_char != '"':
                    result += self.current_char
                    self.advance()
                self.advance()  # consume closing quote
                return Token(TokenType.STRING_LITERAL, result, self.lineno, start_col)
            
            if self.current_char == "'":
                self.advance()
                ch = self.current_char
                self.advance()
                if self.current_char != "'":
                    self.error()
                self.advance()
                return Token(TokenType.CHAR_LITERAL, ch, self.lineno, self.column)

            if self.current_char == '#':
                tok = Token(TokenType.HASH, '#', self.lineno, self.column)
                self.advance()
                return tok

            try:
                tok_type = TokenType(self.current_char)
            except ValueError:
                self.error()
            tok = Token(tok_type, tok_type.value, self.lineno, self.column)
            self.advance()
            return tok

        return Token(TokenType.EOF, None)



###############################################################################
#  PARSER                                                                     #
###############################################################################
class AST:
    pass


class VarDecl(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node


class ArrayDecl(VarDecl):
    def __init__(self, var_node, type_node, size):
        super().__init__(var_node, type_node)
        self.size = size


class ArrayAccess(AST):
    def __init__(self, var_node, index_node):
        self.var_node = var_node
        self.index_node = index_node


class While(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class For(AST):
    def __init__(self, init, condition, post, body):
        self.init = init
        self.condition = condition
        self.post = post
        self.body = body


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Str(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Char(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Print(AST):
    def __init__(self, expr):
        self.expr = expr


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class If(AST):
    def __init__(self, condition, true_branch, false_branch=None):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch


class Compound(AST):
    def __init__(self):
        self.children = []


class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class NoOp(AST):
    pass


class Program(AST):
    def __init__(self, functions, main_block):
        self.functions = functions
        self.main_block = main_block


class Block(AST):
    def __init__(self, declarations, compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement


class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class FunctionDecl(AST):
    def __init__(self, return_type, name, params, body):
        self.return_type = return_type
        self.name = name.value
        self.params = params
        self.body = body


class Param(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node


class FunctionCall(AST):
    def __init__(self, name, actual_params):
        self.name = name.value
        self.actual_params = actual_params


class Return(AST):
    def __init__(self, expr):
        self.expr = expr


class Parser:
    def __init__(self, lexer, base_dir="."):
        self.lexer = lexer
        self.current_token = self.get_next_token()
        self.base_dir = base_dir  # Directory of the main file for resolving includes
        self.included_files = set()  # Track included files to prevent recursive includes

    def get_next_token(self):
        return self.lexer.get_next_token()

    def peek(self):
        saved_pos = self.lexer.pos
        saved_line = self.lexer.lineno
        saved_col = self.lexer.column
        saved_char = self.lexer.current_char

        token = self.lexer.get_next_token()

        self.lexer.pos = saved_pos
        self.lexer.lineno = saved_line
        self.lexer.column = saved_col
        self.lexer.current_char = saved_char
        return token

    def error(self, error_code, token):
        raise ParserError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}',
        )

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.get_next_token()
        else:
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
            )

    def parse_includes(self):
        """Parse #include directives and return function declarations from included files."""
        functions = []
        while self.current_token.type == TokenType.HASH:
            self.eat(TokenType.HASH)
            if self.current_token.type != TokenType.INCLUDE:
                self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
            self.eat(TokenType.INCLUDE)
            
            # Expect a string literal for the filename
            if self.current_token.type != TokenType.STRING_LITERAL:
                self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
            filename = self.current_token.value
            self.eat(TokenType.STRING_LITERAL)
            
            # Make semicolon optional
            if self.current_token.type == TokenType.SEMI:
                self.eat(TokenType.SEMI)
            
            # Resolve the file path relative to the base directory
            file_path = os.path.join(self.base_dir, filename)
            if not os.path.exists(file_path):
                self.error(ErrorCode.FILE_NOT_FOUND, self.current_token, f"File '{filename}' not found")
            
            # Prevent recursive includes
            if file_path in self.included_files:
                continue  # Skip if already included
            self.included_files.add(file_path)
            
            if _SHOULD_LOG_DEBUG:
                print(f"Main: Including file '{filename}'")
            
            # Read and parse the included file
            with open(file_path, 'r') as f:
                included_text = f.read()
            
            # Create a new lexer and a new Parser for the included file
            included_lexer = Lexer(included_text)
            included_parser = Parser(included_lexer, base_dir=self.base_dir)
            included_parser.included_files = self.included_files  # Share the included_files set
            
            # Parse only function declarations from the included file
            while included_parser.current_token.type in (TokenType.INT, TokenType.CHAR, TokenType.STRING, TokenType.VOID, TokenType.FLOAT):
                functions.append(included_parser.function_decl())
        
        return functions

    def program(self):
        if _SHOULD_LOG_DEBUG:
            print("Parser: Parsing program")
        
        # Parse #include directives first
        functions = self.parse_includes()
        
        # Parse function declarations in the current file
        while self.current_token.type in (TokenType.INT, TokenType.CHAR, TokenType.STRING, TokenType.VOID, TokenType.FLOAT):
            if self.current_token.type == TokenType.INT and self.peek().type == TokenType.MAIN:
                break
            functions.append(self.function_decl())

        # Expect 'int main'
        if _SHOULD_LOG_DEBUG:
            print("Parser: Expecting int main")
        self.eat(TokenType.INT)
        self.eat(TokenType.MAIN)
        self.eat(TokenType.LPAREN)
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        decls = self.declarations()
        stmts = self.statement_list()
        self.eat(TokenType.RBRACE)
        comp = Compound()
        comp.children = stmts
        main_block = Block(decls, comp)
        return Program(functions, main_block)
    
    def for_statement(self):
        self.eat(TokenType.FOR)
        self.eat(TokenType.LPAREN)

        # Handle initialization: declaration or assignment
        if self.current_token.type in (TokenType.INT, TokenType.CHAR, TokenType.STRING, TokenType.FLOAT):
            # Initialization is a declaration
            init_nodes = self.declarations()
            if len(init_nodes) == 1:
                init = init_nodes[0]
            else:
                init = Compound()
                init.children = init_nodes
        else:
            # Initialization is an assignment
            init_nodes = []
            while self.current_token.type != TokenType.SEMI:
                init_nodes.append(self.assignment_statement())
                if self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
            if len(init_nodes) == 1:
                init = init_nodes[0]
            else:
                init = Compound()
                init.children = init_nodes
            self.eat(TokenType.SEMI)

        # Parse condition
        condition = self.expr()
        self.eat(TokenType.SEMI)

        # Parse post-expression as a list of assignments
        post_nodes = []
        while self.current_token.type != TokenType.RPAREN:
            post_nodes.append(self.assignment_statement())
            if self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
        if len(post_nodes) == 1:
            post = post_nodes[0]
        else:
            post = Compound()
            post.children = post_nodes
        self.eat(TokenType.RPAREN)

        # Parse body
        body = self.statement()
        return For(init, condition, post, body)
    
    def function_decl(self):
        if _SHOULD_LOG_DEBUG:
            print("Parser: Parsing function declaration")
        return_type = self.type_spec()
        name = self.current_token
        self.eat(TokenType.ID)
        self.eat(TokenType.LPAREN)
        params = []
        if self.current_token.type != TokenType.RPAREN:
            params = self.param_list()
        self.eat(TokenType.RPAREN)
        body = self.compound_statement()
        return FunctionDecl(return_type, name, params, body)

    def param_list(self):
        params = []
        while True:
            param_type = self.type_spec()
            var = self.current_token
            self.eat(TokenType.ID)
            if self.current_token.type == TokenType.LBRACKET:
                self.eat(TokenType.LBRACKET)
                self.eat(TokenType.RBRACKET)
                params.append(Param(Var(var), param_type))
            else:
                params.append(Param(Var(var), param_type))
            if self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
            else:
                break
        return params

    def block(self):
        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(declaration_nodes, compound_statement_node)
        return node

    def declarations(self):
        declarations = []
        while self.current_token.type in (TokenType.INT, TokenType.CHAR, TokenType.STRING, TokenType.FLOAT):
            type_token = self.current_token
            self.eat(type_token.type)
            type_node = Type(type_token)
            while True:
                var_token = self.current_token
                self.eat(TokenType.ID)
                var_node = Var(var_token)
                if self.current_token.type == TokenType.LBRACKET:
                    self.eat(TokenType.LBRACKET)
                    size_token = self.current_token
                    self.eat(TokenType.INTEGER_CONST)
                    self.eat(TokenType.RBRACKET)
                    declarations.append(ArrayDecl(var_node, type_node, size_token.value))
                else:
                    declarations.append(VarDecl(var_node, type_node))
                    if self.current_token.type == TokenType.ASSIGN:
                        self.eat(TokenType.ASSIGN)
                        expr_node = self.expr()
                        assign = Assign(left=var_node, op=Token(TokenType.ASSIGN, '='), right=expr_node)
                        declarations.append(assign)
                if self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                else:
                    break
            self.eat(TokenType.SEMI)
        return declarations

    def type_spec(self):
        token = self.current_token
        if token.type in (TokenType.INT, TokenType.CHAR, TokenType.STRING, TokenType.VOID, TokenType.FLOAT):
            self.eat(token.type)
            return Type(token)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, token)

    def compound_statement(self):
        self.eat(TokenType.LBRACE)
        nodes = self.statement_list()
        self.eat(TokenType.RBRACE)
        root = Compound()
        for node in nodes:
            root.children.append(node)
        return root

    def statement_list(self):
        if _SHOULD_LOG_DEBUG:
            print("Parser: Parsing statement list")
        results = []
        while self.current_token.type not in (TokenType.RBRACE, TokenType.EOF):
            if _SHOULD_LOG_DEBUG:
                print(f"Parser: Current token in statement_list: {self.current_token}")
            stmt = self.statement()
            results.append(stmt)
            if isinstance(stmt, (Assign, Print, FunctionCall, Return)):
                if _SHOULD_LOG_DEBUG:
                    print(f"Parser: Eating semicolon after {type(stmt).__name__}")
                self.eat(TokenType.SEMI)
        if _SHOULD_LOG_DEBUG:
            print(f"Parser: Exiting statement list with token: {self.current_token}")
        return results

    def if_statement(self):
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        condition = self.expr()
        self.eat(TokenType.RPAREN)
        true_branch = self.statement()
        false_branch = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            false_branch = self.statement()
        return If(condition, true_branch, false_branch)

    def while_statement(self):
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        condition = self.expr()
        self.eat(TokenType.RPAREN)
        body = self.statement()
        return While(condition, body)

    def statement(self):
        if _SHOULD_LOG_DEBUG:
            print(f"Parser: Parsing statement, current token: {self.current_token}")
        if self.current_token.type == TokenType.LBRACE:
            node = self.compound_statement()
        elif self.current_token.type == TokenType.IF:
            node = self.if_statement()
        elif self.current_token.type == TokenType.WHILE:
            node = self.while_statement()
        elif self.current_token.type == TokenType.FOR:
            node = self.for_statement()
        elif self.current_token.type == TokenType.PRINT:
            self.eat(TokenType.PRINT)
            self.eat(TokenType.LPAREN)
            expr_node = self.expr()
            self.eat(TokenType.RPAREN)
            node = Print(expr_node)
        elif self.current_token.type == TokenType.RETURN:
            self.eat(TokenType.RETURN)
            expr = self.expr() if self.current_token.type != TokenType.SEMI else NoOp()
            node = Return(expr)
        elif self.current_token.type == TokenType.ID:
            if self.peek().type == TokenType.LPAREN:
                node = self.function_call()
            else:
                node = self.assignment_statement()
        elif self.current_token.type in (TokenType.INT, TokenType.CHAR, TokenType.STRING, TokenType.FLOAT):
            decls = self.declarations()
            if len(decls) == 1:
                node = decls[0]
            else:
                node = Compound()
                node.children = decls
        elif self.current_token.type == TokenType.RBRACE:
            if _SHOULD_LOG_DEBUG:
                print("Parser: Encountered RBRACE in statement, returning NoOp")
            node = NoOp()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
        if _SHOULD_LOG_DEBUG:
            print(f"Parser: Statement parsed, node type: {type(node).__name__}")
        return node

    def function_call(self):
        name = self.current_token
        self.eat(TokenType.ID)
        self.eat(TokenType.LPAREN)
        actual_params = []
        if self.current_token.type != TokenType.RPAREN:
            while True:
                actual_params.append(self.expr())
                if self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                else:
                    break
        self.eat(TokenType.RPAREN)
        return FunctionCall(name, actual_params)

    def assignment_statement(self):
        left = self.variable()
        token = self.current_token
        self.eat(TokenType.ASSIGN)
        right = self.expr()
        node = Assign(left, token, right)
        return node

    def variable(self):
        var_token = self.current_token
        self.eat(TokenType.ID)
        if self.current_token.type == TokenType.LBRACKET:
            self.eat(TokenType.LBRACKET)
            index_expr = self.expr()
            self.eat(TokenType.RBRACKET)
            return ArrayAccess(Var(var_token), index_expr)
        else:
            return Var(var_token)

    def empty(self):
        return NoOp()

    def expr(self):
        node = self.logical_or()
        return node

    def logical_or(self):
        node = self.logical_and()
        while self.current_token.type == TokenType.OR:
            token = self.current_token
            self.eat(TokenType.OR)
            node = BinOp(left=node, op=token, right=self.logical_and())
        return node

    def logical_and(self):
        node = self.comparison()
        while self.current_token.type == TokenType.AND:
            token = self.current_token
            self.eat(TokenType.AND)
            node = BinOp(left=node, op=token, right=self.comparison())
        return node

    def comparison(self):
        node = self.simple_expr()
        if self.current_token.type in (TokenType.EQ, TokenType.NE, TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.simple_expr())
        return node

    def simple_expr(self):
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            node = BinOp(left=node, op=token, right=self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
            elif token.type == TokenType.DIV:
                self.eat(TokenType.DIV)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def factor(self):
        token = self.current_token
        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == TokenType.INTEGER_CONST:
            self.eat(TokenType.INTEGER_CONST)
            return Num(token)
        elif token.type == TokenType.FLOAT_CONST:
            self.eat(TokenType.FLOAT_CONST)
            return Num(token)
        elif token.type == TokenType.STRING_LITERAL:
            self.eat(TokenType.STRING_LITERAL)
            return Str(token)
        elif token.type == TokenType.CHAR_LITERAL:
            self.eat(TokenType.CHAR_LITERAL)
            return Char(token)
        elif token.type == TokenType.ID:
            if self.peek().type == TokenType.LPAREN:
                return self.function_call()
            else:
                var_node = self.variable()
                return var_node
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, token)

    def parse(self):
        node = self.program()
        if self.current_token.type != TokenType.EOF:
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
            )
        return node
    

###############################################################################
#  AST visitors (walkers)                                                     #
###############################################################################

class NodeVisitor:
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


###############################################################################
#  SYMBOLS, TABLES, SEMANTIC ANALYSIS                                         #
###############################################################################

class Symbol:
    def __init__(self, name, type=None):
        self.name = name
        self.type = type
        self.scope_level = 0

    def __str__(self):
        return f'<{self.__class__.__name__}(name={self.name}, type={self.type})>'

    __repr__ = __str__


class VarSymbol(Symbol):
    def __init__(self, name, type):
        super().__init__(name, type)

    def __str__(self):
        return f'<{self.__class__.__name__}(name={self.name}, type={self.type.name if self.type else "None"})>'

    __repr__ = __str__


class FunctionSymbol(Symbol):
    def __init__(self, name, type=None):
        super().__init__(name, type)
        self.params = []  # list of VarSymbol

    def __str__(self):
        return f'<{self.__class__.__name__}(name={self.name}, type={self.type}, params={[str(p) for p in self.params]})>'

    __repr__ = __str__


class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return f'<{self.__class__.__name__}(name={self.name})>'

    __repr__ = __str__


class ScopedSymbolTable:
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self._symbols = {}
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

    def _init_builtins(self):
        self.insert(BuiltinTypeSymbol('int'))
        self.insert(BuiltinTypeSymbol('char'))
        self.insert(BuiltinTypeSymbol('string'))
        self.insert(BuiltinTypeSymbol('void'))
        self.insert(BuiltinTypeSymbol('float'))

    def insert(self, symbol):
        self._symbols[symbol.name] = symbol

    def lookup(self, name, current_scope_only=False):
        symbol = self._symbols.get(name)

        if symbol is not None:
            return symbol

        if current_scope_only:
            return None

        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)

    def log(self):
        if not _SHOULD_LOG_SCOPE:
            return
        heading = f' {self.scope_name.upper()} SCOPE '
        lines = [heading, '=' * len(heading)]
        for k, v in self._symbols.items():
            lines.append(f'{k}: {str(v)}')
        lines.append(f'Enclosing scope: {self.enclosing_scope.scope_name if self.enclosing_scope else "None"}')
        print('\n'.join(lines))


class SemanticAnalyzer(NodeVisitor):
    def __init__(self):
        self.current_scope = None

    def visit_Program(self, node):
        global_scope = ScopedSymbolTable('global', 1, None)
        global_scope._init_builtins()
        self.current_scope = global_scope

        for func in node.functions:
            self.visit(func)

        self.visit(node.main_block)

        global_scope.log()  # Log the global scope after full analysis

        self.current_scope = None

    def visit_FunctionDecl(self, node):
        func_name = node.name
        func_symbol = FunctionSymbol(func_name)

        self.current_scope.insert(func_symbol)

        func_scope = ScopedSymbolTable(scope_name=func_name, scope_level=self.current_scope.scope_level + 1, enclosing_scope=self.current_scope)

        self.current_scope = func_scope

        for param in node.params:
            param_type = self.current_scope.lookup(param.type_node.value)
            param_name = param.var_node.value
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.insert(var_symbol)
            func_symbol.params.append(var_symbol)

        self.visit(node.body)

        func_scope.log()  # Log the function scope after analysis

        self.current_scope = self.current_scope.enclosing_scope

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.current_scope.lookup(type_name)
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)
        self.current_scope.insert(var_symbol)

    def visit_ArrayDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.current_scope.lookup(type_name)
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)
        self.current_scope.insert(var_symbol)

    def visit_Assign(self, node):
        right_value = self.visit(node.right)
        left_var = self.visit(node.left)
        if isinstance(node.left, Var):
            var_symbol = self.current_scope.lookup(node.left.value)
            if var_symbol.type.name == 'int' and isinstance(right_value, float):
                raise SemanticError(message=f"Cannot assign float to int variable {node.left.value}", token=node.left.token)
        self.visit(node.right)
        self.visit(node.left)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise SemanticError(ErrorCode.ID_NOT_FOUND, node.token)

    def visit_Num(self, node):
        pass

    def visit_Str(self, node):
        pass  # String literals require no semantic checks

    def visit_Char(self, node):
        pass  # Character literals require no semantic checks

    def visit_UnaryOp(self, node):
        self.visit(node.expr)

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_Print(self, node):
        self.visit(node.expr)

    def visit_If(self, node):
        self.visit(node.condition)
        self.visit(node.true_branch)
        if node.false_branch:
            self.visit(node.false_branch)

    def visit_While(self, node):
        self.visit(node.condition)
        self.visit(node.body)

    def visit_For(self, node):
        self.visit(node.init)
        self.visit(node.condition)
        self.visit(node.post)
        self.visit(node.body)

    def visit_Return(self, node):
        if node.expr is not None:
            self.visit(node.expr)

    def visit_FunctionCall(self, node):
        func_symbol = self.current_scope.lookup(node.name)
        if func_symbol is None:
            raise SemanticError(ErrorCode.ID_NOT_FOUND, node.name)

        if len(func_symbol.params) != len(node.actual_params):
            raise SemanticError(ErrorCode.ARG_COUNT_MISMATCH, node.name)

        for param in node.actual_params:
            self.visit(param)

    def visit_ArrayAccess(self, node):
        self.visit(node.var_node)
        self.visit(node.index_node)

###############################################################################
#  INTERPRETER                                                                #
###############################################################################


class ARType(Enum):
    PROGRAM = 'PROGRAM'
    FUNCTION = 'FUNCTION'


class CallStack:
    def __init__(self):
        self._records = []

    def push(self, ar):
        self._records.append(ar)

    def pop(self):
        return self._records.pop()

    def peek(self):
        return self._records[-1]

    def log(self):
        if not _SHOULD_LOG_STACK:
            return
        print('\nCALL STACK:')
        for ar in self._records[::-1]:  # Reversed to show top of stack first
            print(ar)
            print('---')


class ActivationRecord:
    def __init__(self, name, type, nesting_level):
        self.name = name
        self.type = type
        self.nesting_level = nesting_level
        self.members = {}

    def __getitem__(self, key):
        return self.members[key]

    def __setitem__(self, key, value):
        self.members[key] = value

    def get(self, key):
        return self.members.get(key)

    def __str__(self):
        lines = [
            f'AR {self.type.name} {self.name} level {self.nesting_level}',
            '=' * 40,
        ]
        for k, v in sorted(self.members.items()):
            lines.append(f'{k}: {v}')
        return '\n'.join(lines)

    __repr__ = __str__


class Interpreter(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.call_stack = CallStack()

    def visit_Program(self, node):
        ar = ActivationRecord(
            name='global',
            type=ARType.PROGRAM,
            nesting_level=1,
        )
        self.call_stack.push(ar)
        if _SHOULD_LOG_STACK:
            print('ENTER PROGRAM')
        self.call_stack.log()

        for function in node.functions:
            ar.members[function.name] = function  # Use ar.members instead of ar[key]

        self.visit(node.main_block)

        if _SHOULD_LOG_STACK:
            print('LEAVE PROGRAM')
        self.call_stack.log()
        self.call_stack.pop()

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node):
        ar = self.call_stack.peek()
        var_name = node.var_node.value
        var_type = node.type_node.value.lower()

        if var_type == 'char':
            ar.members[var_name] = '\0'
        elif var_type == 'string':
            ar.members[var_name] = ''
        elif var_type == 'float':
            ar.members[var_name] = 0.0
        else:
            ar.members[var_name] = 0
        if _SHOULD_LOG_DEBUG:
            print(f"Interpreter: Declared {var_name} of type {var_type}")

    def visit_ArrayDecl(self, node):
        ar = self.call_stack.peek()
        var_name = node.var_node.value
        var_type = node.type_node.value.lower()

        if var_type == 'char':
            ar.members[var_name] = ['\0'] * node.size
        elif var_type == 'string':
            ar.members[var_name] = [''] * node.size
        elif var_type == 'float':
            ar.members[var_name] = [0.0] * node.size
        else:
            ar.members[var_name] = [0] * node.size
        if _SHOULD_LOG_DEBUG:
            print(f"Interpreter: Declared array {var_name} of type {var_type} size {node.size}")

    def visit_FunctionCall(self, node):
        if _SHOULD_LOG_DEBUG:
            print(f"Interpreter: Visiting FunctionCall node for {node.name}")
        
        # Search the call stack for the function, starting from the current scope
        func_decl = None
        for ar in reversed(self.call_stack._records):
            func_decl = ar.members.get(node.name)
            if func_decl:
                break
        if not func_decl:
            raise Exception(f"Function {node.name} not found")

        ar = ActivationRecord(
            name=node.name,
            type=ARType.FUNCTION,
            nesting_level=self.call_stack.peek().nesting_level + 1,
        )

        for param, arg in zip(func_decl.params, node.actual_params):
            ar.members[param.var_node.value] = self.visit(arg)

        self.call_stack.push(ar)
        if _SHOULD_LOG_STACK:
            print(f'ENTER FUNCTION {node.name}')
        self.call_stack.log()

        try:
            self.visit(func_decl.body)
            result = None  # Default for void functions
        except ReturnException as e:
            result = e.value

        if _SHOULD_LOG_STACK:
            print(f'LEAVE FUNCTION {node.name} return {result}')
        self.call_stack.log()
        self.call_stack.pop()
        if _SHOULD_LOG_DEBUG:
            print(f"Interpreter: Function {node.name} returned {result}")
        return result

    def visit_Compound(self, node):
        if _SHOULD_LOG_DEBUG:
            print("Interpreter: Visiting Compound node")
        for child in node.children:
            try:
                self.visit(child)
            except ReturnException as e:
                if _SHOULD_LOG_DEBUG:
                    print(f"Interpreter: Caught ReturnException with value {e.value}")
                raise  # Propagate the return value up

    def visit_Return(self, node):
        value = self.visit(node.expr) if node.expr else None
        raise ReturnException(value)

    def visit_NoOp(self, node):
        pass

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op.type
        if op == TokenType.PLUS:
            return left + right
        elif op == TokenType.MINUS:
            return left - right
        elif op == TokenType.MUL:
            return left * right
        if op == TokenType.DIV:
            if right == 0:
                raise Exception("Division by zero")
            return left / right
        elif op == TokenType.EQ:
            return left == right
        elif op == TokenType.NE:
            return left != right
        elif op == TokenType.LT:
            return left < right
        elif op == TokenType.LE:
            return left <= right
        elif op == TokenType.GT:
            return left > right
        elif op == TokenType.GE:
            return left >= right
        elif op == TokenType.AND:
            return left and right
        elif op == TokenType.OR:
            return left or right

    def visit_Num(self, node):
        return node.value

    def visit_Str(self, node):
        return node.value

    def visit_Char(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == TokenType.PLUS:
            return +self.visit(node.expr)
        elif op == TokenType.MINUS:
            return -self.visit(node.expr)

    def visit_Assign(self, node):
        ar = self.call_stack.peek()
        value = self.visit(node.right)

        if isinstance(node.left, ArrayAccess):
            array_name = node.left.var_node.value
            index = self.visit(node.left.index_node)

            array = ar.members.get(array_name)  # Use members.get
            if not isinstance(array, list):
                raise Exception(f"{array_name} is not an array")

            if not isinstance(index, int) or index < 0 or index >= len(array):
                raise Exception(f"Index {index} out of bounds for array '{array_name}'")

            array[index] = value
            if _SHOULD_LOG_DEBUG:
                print(f"Interpreter: Assigned {array_name}[{index}] = {value}")
        else:
            var_name = node.left.value
            ar.members[var_name] = value  # Use ar.members
            if _SHOULD_LOG_DEBUG:
                print(f"Interpreter: Assigned {var_name} = {value}")

    def visit_Var(self, node):
        var_name = node.value
        ar = self.call_stack.peek()
        return ar.members.get(var_name)  # Use members.get
    
    def visit_ArrayAccess(self, node):
        array_name = node.var_node.value
        index = self.visit(node.index_node)
        ar = self.call_stack.peek()
        array = ar.get(array_name)
        if not isinstance(array, list):
            raise Exception(f"{array_name} is not an array")
        if not isinstance(index, int) or index < 0 or index >= len(array):
            raise Exception(f"Index {index} out of bounds for array '{array_name}'")
        return array[index]

    def visit_Print(self, node):
        print(self.visit(node.expr))

    def visit_If(self, node):
        if self.visit(node.condition):
            self.visit(node.true_branch)
        elif node.false_branch:
            self.visit(node.false_branch)

    def visit_While(self, node):
        while self.visit(node.condition):
            self.visit(node.body)

    def visit_For(self, node):
        # Execute initialization
        if isinstance(node.init, Compound):
            for child in node.init.children:
                self.visit(child)
        else:
            self.visit(node.init)
        
        # Loop with condition and post-expression
        while self.visit(node.condition):
            self.visit(node.body)
            if isinstance(node.post, Compound):
                for post_stmt in node.post.children:
                    self.visit(post_stmt)
            else:
                self.visit(node.post)

    def interpret(self):
        tree = self.tree
        if tree is None:
            return ''
        return self.visit(tree)


def main():
    parser = argparse.ArgumentParser(description='CLIKE - C-like Interpreter')
    parser.add_argument('inputfile', help='C-like source file')
    parser.add_argument('--scope', help='Print scope information', action='store_true')
    parser.add_argument('--stack', help='Print call stack', action='store_true')
    parser.add_argument('--debug', help='Print debug information during execution', action='store_true')
    args = parser.parse_args()

    global _SHOULD_LOG_SCOPE, _SHOULD_LOG_STACK, _SHOULD_LOG_DEBUG
    _SHOULD_LOG_SCOPE = args.scope
    _SHOULD_LOG_STACK = args.stack
    _SHOULD_LOG_DEBUG = args.debug

    try:
        with open(args.inputfile, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.inputfile}' not found")
        sys.exit(1)

    if _SHOULD_LOG_DEBUG:
        print(f"Main: Reading input file '{args.inputfile}'")

    # Get the directory of the input file for resolving includes
    base_dir = os.path.dirname(args.inputfile) or "."
    lexer = Lexer(text)
    try:
        if _SHOULD_LOG_DEBUG:
            print("Main: Starting lexer and parser")
        parser = Parser(lexer, base_dir=base_dir)
        tree = parser.parse()
    except (LexerError, ParserError) as e:
        print(f"Error during parsing: {e.message}")
        sys.exit(1)

    if _SHOULD_LOG_DEBUG:
        print("Main: Starting semantic analysis")
    semantic_analyzer = SemanticAnalyzer()
    try:
        semantic_analyzer.visit(tree)
    except SemanticError as e:
        print(f"Error during semantic analysis: {e.message}")
        sys.exit(1)

    if _SHOULD_LOG_DEBUG:
        print("Main: Starting interpreter")
    interpreter = Interpreter(tree)
    interpreter.interpret()
    if _SHOULD_LOG_DEBUG:
        print("Main: Interpretation completed")

if __name__ == '__main__':
    main()