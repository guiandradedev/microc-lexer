from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Iterator


class TokenKind(enum.Enum):
    """Classe já implementada: nomes e números não devem ser alterados."""

    EOF = -1

    IDENTIFIER = 1
    INT_LITERAL = 2
    STRING_LITERAL = 3

    KW_INT = 10
    KW_BOOL = 11
    KW_VOID = 12
    KW_TRUE = 13
    KW_FALSE = 14
    KW_IF = 15
    KW_ELSE = 16
    KW_WHILE = 17
    KW_RETURN = 18
    KW_PRINT = 19

    PLUS = 20
    MINUS = 21
    STAR = 22
    SLASH = 23
    PERCENT = 24
    LESS = 25
    LESS_EQUAL = 26
    GREATER = 27
    GREATER_EQUAL = 28
    EQUAL_EQUAL = 29
    NOT_EQUAL = 30
    LOGICAL_AND = 31
    LOGICAL_OR = 32
    LOGICAL_NOT = 33
    ASSIGN = 34

    LEFT_PAREN = 40
    RIGHT_PAREN = 41
    LEFT_BRACE = 42
    RIGHT_BRACE = 43
    COMMA = 44
    SEMICOLON = 45


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    lexeme: str
    value: int | str | bool | None
    line: int
    column: int

    def __str__(self) -> str:
        return (
            f"<{self.kind.value}, {self.kind.name}, {self.lexeme!r}, "
            f"{self.value!r}, {self.line}, {self.column}>"
        )


class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return f"erro léxico em {self.line}:{self.column}: {self.message}"


class Lexer:
    """Converte texto-fonte MicroC em uma sequência de tokens."""

    """ transition_table = {
        "estado": {
            "caractere": {
                "next_state": "novo_estado",
            }
        },
        "novo_estado": {
            "caractere": {
                "next_state": "novo_estado",
                "token": TokenKind.IDENTIFIER  # Se existir atributo token, é final; caso contrário é intermediario
            }
        }
    } """
    
    

    def ignored_char(self, char):
        if char != '\0':
            self.advance()
            return None
    
    def token_start(self, char):
        self.start_line, self.start_column = self.line, self.column
        self.lexema = char
        self.advance()
        return None
        
    def start_string(self, char):
        self.start_line, self.start_column = self.line, self.column
        self.lexema, self.string_value = char, ""
        self.advance()
        return None
    
    def start_string_escape(self, char):
        self.escape_column = self.column
        self.lexema += char
        self.advance()
        return None
    
    def escape_char(self, char, decoded_char):
        self.lexema += char
        self.string_value += decoded_char
        self.advance()
        return None
    
    def accumulate(self, char):
        self.lexema += char
        self.advance()
        return None

    def accumulate_both(self, char):
        self.lexema += char
        self.string_value += char
        self.advance()
        return None
    
    
    def define_id(self, char):
        kind = self.keywords.get(self.lexema, TokenKind.IDENTIFIER)
        val = None
        if kind == TokenKind.KW_TRUE:
            val = True
        elif kind == TokenKind.KW_FALSE:
            val = False
            
        if kind == TokenKind.IDENTIFIER:
            val = self.lexema
        return Token(kind, self.lexema, val, self.start_line, self.start_column)

    
    def define_int(self, char):
        return Token(TokenKind.INT_LITERAL, self.lexema, int(self.lexema), self.start_line, self.start_column)

    def define_string(self, char):
        self.lexema += char
        self.advance()
        return Token(TokenKind.STRING_LITERAL, self.lexema, self.string_value, self.start_line, self.start_column)

    def one_char_transition(self, char, tokenKind):
        self.start_line, self.start_column = self.line, self.column
        self.advance()
        return Token(tokenKind, char, None, self.start_line, self.start_column)

    def double_char_transition(self, char, tokenKind):
        self.lexema += char
        self.advance()
        return Token(tokenKind, self.lexema, None, self.start_line, self.start_column)

    def end_of_file(self, char):
        return Token(TokenKind.EOF, "", None, self.line, self.column) 

    def unknown_char(self, char):
        return LexerError(self.line, self.column, "Unknown character: " + char)

    def fallback(self, tokenKind):
        return Token(tokenKind, self.lexema, None, self.start_line, self.start_column)


    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.length = len(source)
        self.line = 1
        self.column = 1
        
        self.state = 'start'
        self.lexema = ""
        self.string_value = ""
        self.start_line = 1
        self.start_column = 1
        self.escape_column = 1
        
        self.keywords = {
            'int': TokenKind.KW_INT, 'bool': TokenKind.KW_BOOL, 'void': TokenKind.KW_VOID,
            'true': TokenKind.KW_TRUE, 'false': TokenKind.KW_FALSE, 'if': TokenKind.KW_IF,
            'else': TokenKind.KW_ELSE, 'while': TokenKind.KW_WHILE, 'return': TokenKind.KW_RETURN,
            'print': TokenKind.KW_PRINT
        }
        
        # TODO: Scape, comentario

        # Default: transição inváida
        self.transitions_table = {          # estado: {classe: (proximo estado, acao)}
                'start': {  
                    # Special chars
                    'space': ('start',      self.ignored_char),
                    'newline': ('start',    self.ignored_char), # New line não seria \n?

                    # Individual char
                    '(': ('start',      lambda c: self.one_char_transition(c, TokenKind.LEFT_PAREN)),
                    ')': ('start',      lambda c: self.one_char_transition(c, TokenKind.RIGHT_PAREN)),
                    '{': ('start',      lambda c: self.one_char_transition(c, TokenKind.LEFT_BRACE)),
                    '}': ('start',      lambda c: self.one_char_transition(c, TokenKind.RIGHT_BRACE)),
                    '%': ('start',      lambda c: self.one_char_transition(c, TokenKind.PERCENT)),
                    '+': ('start',      lambda c: self.one_char_transition(c, TokenKind.PLUS)),
                    '-': ('start',      lambda c: self.one_char_transition(c, TokenKind.MINUS)),
                    '*': ('start',      lambda c: self.one_char_transition(c, TokenKind.STAR)),
                    ',': ('start',      lambda c: self.one_char_transition(c, TokenKind.COMMA)),
                    ';': ('start',      lambda c: self.one_char_transition(c, TokenKind.SEMICOLON)),

                    # Double char
                    '>': ('greater',    self.token_start),
                    '<': ('less',       self.token_start),
                    '=': ('equal',      self.token_start),
                    '!': ('not',        self.token_start),
                    '|': ('or',         self.token_start),
                    '&': ('and',        self.token_start),
                    
                    '/': ('slash',      self.token_start),
                    '"': ('string',     self.start_string),

                    # Identifiers
                    'digit': ('int',        self.token_start),
                    'char': ('id',          self.token_start), # Validate if is char or _
                    
                    'eof': ('end',          self.end_of_file),
                    'default': ('error',    self.unknown_char)
                },
                
                'slash': {
                    # '/': ('line_comment', lambda c: self.ignored_char(c, None)),
                    # '*': ('block_comment', lambda c: self.ignored_char(c, None)),
                    'default': ('start', lambda c: self.fallback(c, TokenKind.SLASH)) # nao consumir no fallback
                },
                
                # Operadores compostos (maior prefixo)
                'greater': {
                    '=': ('start',      lambda c: self.double_char_transition(c, TokenKind.GREATER_EQUAL)),
                    'default': ('start',lambda c: self.fallback(TokenKind.GREATER))
                },
                'less': {
                    '=': ('start',      lambda c: self.double_char_transition(c, TokenKind.LESS_EQUAL)),
                    'default': ('start',lambda c: self.fallback(TokenKind.LESS))
                },
                'equal': {
                    '=': ('start',      lambda c: self.double_char_transition(c, TokenKind.EQUAL_EQUAL)),
                    'default': ('start',lambda c: self.fallback(TokenKind.ASSIGN))
                },
                'not': {
                    '=': ('start',      lambda c: self.double_char_transition(c, TokenKind.NOT_EQUAL)),
                    'default': ('start',lambda c: self.fallback(TokenKind.NOT))
                },
                'or': {
                    '|': ('start',      lambda c: self.double_char_transition(c, TokenKind.LOGICAL_OR)),
                    'default': ('error',lambda c: self.unknown_char(c))
                },
                'and': {
                    '&': ('start',      lambda c: self.double_char_transition(c, TokenKind.LOGICAL_AND)),
                    'default': ('error',lambda c: self.unknown_char(c))
                },
                
                
                'int': {
                    'digit': ('int',            self.accumulate),
                    'default': ('start',        self.define_int)
                },
                'id': {
                    'digit': ('id',             self.accumulate),
                    'char': ('id',              self.accumulate),
                    'default': ('start',        self.define_id)
                },
                
                
                'string': {
                    '"': ('start',              self.define_string),
                    '\\': ('string_escape',     self.start_string_escape),
                    'newline': ('error',        self.unknown_char),
                    'eof': ('error',            self.unknown_char),
                    'default': ('string',       self.accumulate_both)
                },
                'string_escape': {
                    'n': ('string',             lambda c: self.escape_char(c, '\n')),
                    't': ('string',             lambda c: self.escape_char(c, '\t')),
                    '"': ('string',             lambda c: self.escape_char(c, '"')),
                    '\\': ('string',            lambda c: self.escape_char(c, '\\')),
                    'eof': ('error',            self.unknown_char),
                    'default': ('error',        self.unknown_char)
                },
            }

    def peek(self) -> str:
        """Retorna caractere sem consumi-lo, ou None se EOF."""
        if self.pos >= self.length:
            return '\0'
        return self.source[self.pos]

    def advance(self):
        """Consume o próximo caractere"""
        if self.pos < len(self.source):
            char = self.source[self.pos]
            self.pos += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
                
    def char_class(self, char: str) -> str:
        if char == '\0': return 'eof'
        if char == '\n': return 'newline'
        if char.isspace(): return 'space'
        if char.isdigit(): return 'digit'
        if char.isalpha() or char == '_': return 'char'
        return char

    def tokens(self) -> Iterator[Token]:
        """Produza todos os tokens significativos e um único EOF ao final."""

# if transition is None:
#     transition = self.transitions_table[self.state].get('default')

        # Percorrer o texto
        while self.pos < len(self.source):
            symbol = self.peek()
            if not symbol.isascii():
                self.state = 'error'
                break

            key = ""
            if symbol.isalpha():
                key = "char"
            elif symbol.isdigit():
                key = "digit"
            elif symbol.isspace():
                key = "space"
            else:
                key = symbol

            if self.state == "string":
                # Permite qualquer caracter alphanumerico
                print("a")

            transition = self.transitions_table[self.state].get(key)

            if transition is None:
                # default_state, default_action = self.transitions_table[self.state]['default']
                # default_action(symbol)
                # new_state = default_state
                print(transition)
            else:
                new_state, action = transition
                action(symbol)

            self.state = new_state
            self.advance()
            
        yield  # mantém este método como gerador durante o desenvolvimento

    def scan(self) -> list[Token]:
        tokens = []
        
        while self.state != 'end':
            char = self.peek()
            
            if char != '\0' and ord(char) > 127:
                raise LexerError("Caractere nao ascii", self.line, self.column)
            
            c_class = self.char_class(char)
            state_transition = self.transitions_table[self.state]
            
            if c_class in state_transition:
                next_state, action = state_transition[c_class]
            elif 'default' in state_transition:
                next_state, action = state_transition['default']
            else:
                raise LexerError("Transição não encontrada", self.line, self.column)
            
            token = action(char)
            self.state = next_state
            
            if token:
                tokens.append(token)
                
        return tokens