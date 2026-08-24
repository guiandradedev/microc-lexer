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

    # transition_table = {
    #     "estado": {
    #         "caractere": {
    #             "next_state": "novo_estado",
    #         }
    #     },
    #     "novo_estado": {
    #         "caractere": {
    #             "next_state": "novo_estado",
    #             "token": TokenKind.IDENTIFIER  # Se existir atributo token, é final; caso contrário é intermediario
    #         }
    #     }
    # }

    keyworlds = {
        'int': TokenKind.KW_INT,
        'true': TokenKind.KW_TRUE,
        'false': TokenKind.KW_FALSE,
    }
    
    # single_char = {
    #     '+': TokenKind.PLUS,
    #     '-': TokenKind.MINUS,
    #     '*': TokenKind.STAR,
    #     '/': TokenKind.SLASH,
    #     '%': TokenKind.PERCENT,
    #     '(': TokenKind.LEFT_PAREN,
    #     ')': TokenKind.RIGHT_PAREN,
    #     '{': TokenKind.LEFT_BRACE,
    #     '}': TokenKind.RIGHT_BRACE,
    #     ',': TokenKind.COMMA,
    #     ';': TokenKind.SEMICOLON
    # }
    
    

    def ignored_char(self, char, tokenKind):
        pass

    def one_char_transition(self, char, tokenKind):
        # return Token(tokenKind, )
        return char

    def double_char_transition(self, char, tokenKind):
        if tokenKind != None:
            print('dc', char, tokenKind)
            print(char)

    def token_content(self, char, tokenKind):
        if tokenKind != None:
            print('tc', char, tokenKind)


    def token_content_string(self, char, tokenKind):
        if tokenKind != None:
            print('tcs', char, tokenKind)


    def end_of_file(self, char, tokenKind):
        pass


    def unknown_char(self, char, tokenKind):
        pass


    def fallback(self, char, tokenKind):
        pass


    def __init__(self, source: str):
        self.source = source
        self.pos = 0

        # Scape, comentario

        # Default: transição inváida
        self.transitions_table = {
                'start': {  
                    # Special chars
                    'space': ('start', lambda c: self.ignored_char(c, None)),
                    # 'newline': ('start', lambda c: self.ignored_char(c, None)), # New line não seria \n?

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
                    '>': ('greater',    lambda c: self.double_char_transition(c, TokenKind.GREATER)),
                    '<': ('less',       lambda c: self.double_char_transition(c, TokenKind.LESS)),
                    '=': ('equal',      lambda c: self.double_char_transition(c, TokenKind.ASSIGN)),
                    '!': ('not',        lambda c: self.double_char_transition(c, TokenKind.LOGICAL_NOT)),
                    '|': ('or',         lambda c: self.double_char_transition(c, TokenKind.LOGICAL_OR)),
                    '&': ('and',        lambda c: self.double_char_transition(c, TokenKind.LOGICAL_AND)),

                    # Identifiers
                    'digit': ('int',    lambda c: self.token_content(c, TokenKind.INT_LITERAL)),
                    'char': ('char',    lambda c: self.token_content(c, TokenKind.IDENTIFIER)), # Validate if is char or _
                    '"': ('string',     lambda c: self.token_content_string(c, TokenKind.STRING_LITERAL)),
                    '/': ('slash',      lambda c: self.token_content(c, TokenKind.SLASH)), # !!!! como apagar comentario
                    
                    None: ('eof',      lambda c: self.end_of_file(c, TokenKind.EOF)),
                    'default': ('error',lambda c: self.unknown_char(c))
                },
                
                'slash': {
                    # '/': ('line_comment', lambda c: self.ignored_char(c, None)),
                    # '*': ('block_comment', lambda c: self.ignored_char(c, None)),
                    'default': ('start', lambda c: self.fallback(c, TokenKind.SLASH)) # nao consumir no fallback
                },
                # 'slash': {
                #     '/': ('line_comment', lambda c: self.ignored_char(c, None)),
                #     '*': ('block_comment', lambda c: self.ignored_char(c, None)),
                #     'default': ('start', lambda c: self.fallback(c, TokenKind.SLASH)) # nao consumir no fallback
                # },
                'greater': {
                    '=': ('start',      lambda c: self.double_char_transition(c, TokenKind.GREATER_EQUAL)),
                    'default': ('error',lambda c: self.unknown_char(c))
                },
                'less': {
                    '=': ('start',      lambda c: self.double_char_transition(c, TokenKind.LESS_EQUAL)),
                    'default': ('error',lambda c: self.unknown_char(c))
                },
                'equal': {
                    '=': ('start',      lambda c: self.double_char_transition(c, TokenKind.EQUAL_EQUAL)),
                    'default': ('error',lambda c: self.unknown_char(c))
                },
                'not': {
                    '=': ('start',      lambda c: self.double_char_transition(c, TokenKind.NOT_EQUAL)),
                    'default': ('error',lambda c: self.unknown_char(c))
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
                    'digit': ('int',    lambda c: self.token_content(c, TokenKind.INT_LITERAL)),
                    'default': ('error',lambda c: self.unknown_char(c))
                },
                'char': {
                    'digit': ('char',   lambda c: self.token_content(c, TokenKind.IDENTIFIER)),
                    'char': ('char',    lambda c: self.token_content(c, TokenKind.IDENTIFIER)),
                    'default': ('error',lambda c: self.unknown_char(c))
                },
                'string': {
                    # '(': ('string',     lambda c: self.token_content_string(c, None)),
                    # ')': ('string',     lambda c: self.token_content_string(c, None)),
                    # '{': ('string',     lambda c: self.token_content_string(c, None)),
                    # '}': ('string',     lambda c: self.token_content_string(c, None)),
                    # '%': ('string',     lambda c: self.token_content_string(c, None)),
                    # '+': ('string',     lambda c: self.token_content_string(c, None)),
                    # '-': ('string',     lambda c: self.token_content_string(c, None)),
                    # '*': ('string',     lambda c: self.token_content_string(c, None)),
                    # ',': ('string',     lambda c: self.token_content_string(c, None)),
                    # ';': ('string',     lambda c: self.token_content_string(c, None)),

                    # '>': ('string',     lambda c: self.token_content_string(c, None)),
                    # '<': ('string',     lambda c: self.token_content_string(c, None)),
                    # '=': ('string',     lambda c: self.token_content_string(c, None)),
                    # '!': ('string',     lambda c: self.token_content_string(c, None)),
                    # '|': ('string',     lambda c: self.token_content_string(c, None)),
                    # '&': ('string',     lambda c: self.token_content_string(c, None)),

                    # 'digit': ('string', lambda c: self.token_content_string(c, None)),
                    # 'char': ('string',  lambda c: self.token_content_string(c, None)),
                    # '/': ('string',     lambda c: self.token_content_string(c, None)),

                    # Se for alphanumerico aceita
                    '"': ('start',      lambda c: self.token_content_string(c, TokenKind.STRING_LITERAL)),
                },
                'eof': {},
                'error': {}
            }


        self.state = 'start'
        # TODO: inicialize aqui o estado exigido por sua estratégia.
        # Percorre digitos:
        # Enquanto state != EOF
        #     dig = peek()
        #     se ischar(dig):
        #         key = char
        #     se nao isdig(dig):
        #         key = dig

        #     new_state = self.transition_table[state][key]
        #     se new_state != undefined:
        #           # Adiciona o ultimo token lido na lista
        #     se nao:
        #         state = start
        #       advance()

    def peek(self) -> str | None:
        """Retorna o próximo caractere sem consumi-lo, ou None se EOF."""
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def advance(self) -> str | None:
        """Consume o próximo caractere e retorna-o, ou None se EOF."""
        if self.pos < len(self.source):
            char = self.source[self.pos]
            self.pos += 1
            return char
        return None

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
        return list(self.tokens())