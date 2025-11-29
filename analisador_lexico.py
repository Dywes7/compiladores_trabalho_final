from tabulate import tabulate
import reprlib

# Palavras reservadas
palavras_reservadas = {
    "int": "INT",
    "float": "FLOAT",
    "char": "CHAR",
    "double": "DOUBLE",
    "void": "VOID",
    "string": "STRING",
    "return": "RETURN",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "do": "DO",
    "switch": "SWITCH",
    "case": "CASE",
    "default": "DEFAULT",
    "break": "BREAK",
    "continue": "CONTINUE",
    "struct": "STRUCT",
    "typedef": "TYPEDEF",
    "sizeof": "SIZEOF",
    "goto": "GOTO",
}

# Operadores/Delimitadores de 1 caractere
mapa = {
    "=": "EQUAL",
    "+": "PLUS",
    "-": "MINUS",
    "*": "TIMES",
    "/": "DIVIDE",
    "%": "MOD",
    "<": "LT",
    ">": "GT",
    "!": "NOT",
    ";": "SEMI",
    ",": "COMMA",
    ".": "DOT",
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    "[": "LBRACK",
    "]": "RBRACK",
}

# Operadores/Delimitadores de 2 caracteres
mapa2 = {
    "==": "EQ",
    "!=": "NE",
    "<=": "LE",
    ">=": "GE",
    "&&": "AND",
    "||": "OR",
    "+=": "PLUSEQ",
    "-=": "MINUSEQ",
    "*=": "TIMESEQ",
    "/=": "DIVEQ",
    "%=": "MODEQ",
    "->": "ARROW",
    "++": "INC",
    "--": "DEC",
}

categorias = {
    # comparação
    "EQ": "Operador de comparação",
    "NE": "Operador de comparação",
    "LE": "Operador de comparação",
    "GE": "Operador de comparação",
    "LT": "Operador de comparação",
    "GT": "Operador de comparação",

    # aritméticos
    "PLUS": "Operador aritmético",
    "MINUS": "Operador aritmético",
    "TIMES": "Operador aritmético",
    "DIVIDE": "Operador aritmético",

    # atribuição
    "EQUAL": "Operador de atribuição",
    "PLUSEQ": "Operador de atribuição",
    "MINUSEQ": "Operador de atribuição",
    "TIMESEQ": "Operador de atribuição",
    "DIVEQ": "Operador de atribuição",
    "MODEQ": "Operador de atribuição",
    "INC": "Operador de atribuição",
    "DEC": "Operador de atribuição",

    # símbolos especiais
    "SEMI": "Símbolo especial",
    "COMMA": "Símbolo especial",
    "LPAREN": "Símbolo especial",
    "RPAREN": "Símbolo especial",
    "LBRACE": "Símbolo especial",
    "RBRACE": "Símbolo especial",
    "LBRACK": "Símbolo especial",
    "RBRACK": "Símbolo especial",
    "DOT": "Símbolo especial",
    "ELLIPSIS": "Símbolo especial",

    # erro
    "BADNUMID": "Erro léxico (número malformado)",
    "ERROR": "Erro léxico",

    # identificador
    "ID": "Identificador",

    # número genérico
    "NUM": "Número",

    # TEXTO / CARACTERE
    "TEXTO": "Constante de texto",
    "CHAR_LITERAL": "Constante de caractere",

    # Diretivas
    "PP_DIRECTIVE": "Diretiva de pré-processamento",

    # lógicos
    "AND": "Operador lógico",
    "OR": "Operador lógico",
    "NOT": "Operador lógico",

    # acesso
    "ARROW": "Operador de acesso",
}


class Token:
    def __init__(self, tipo, lexema, linha, coluna, atributo=None):
        self.tipo = tipo
        self.lexema = lexema
        self.atributo = atributo
        self.linha = linha
        self.coluna = coluna


def analisar_lexema(codigo_fonte):
    tabela_simbolos = {}
    lista_tokens = []
    ponteiro = 0
    tamanho_codigo = len(codigo_fonte)

    linha = 1
    coluna = 1

    def atualiza_pos(inicio, fim, linha_atual, coluna_atual):
        """Atualiza linha/coluna com base nos caracteres consumidos entre [inicio, fim)."""
        for ch in codigo_fonte[inicio:fim]:
            if ch == "\n":
                linha_atual += 1
                coluna_atual = 1
            else:
                coluna_atual += 1
        return linha_atual, coluna_atual

    while ponteiro < tamanho_codigo:
        caractere_atual = codigo_fonte[ponteiro]

        # 1. Espaços em branco
        if caractere_atual.isspace():
            if caractere_atual == "\n":
                linha += 1
                coluna = 1
            else:
                coluna += 1
            ponteiro += 1
            continue

        # Diretiva de pré-processamento (# no início lógico da linha)
        if codigo_fonte.startswith("#", ponteiro):
            k = ponteiro - 1
            inicio_de_linha = True
            while k >= 0 and codigo_fonte[k] != "\n":
                if codigo_fonte[k] not in (" ", "\t"):
                    inicio_de_linha = False
                    break
                k -= 1
            if inicio_de_linha:
                inicio = ponteiro
                linha_tok = linha
                coluna_tok = coluna
                while ponteiro < tamanho_codigo and codigo_fonte[ponteiro] != "\n":
                    ponteiro += 1
                lexema = codigo_fonte[inicio:ponteiro]
                lista_tokens.append(Token("PP_DIRECTIVE", lexema, linha_tok, coluna_tok))
                linha, coluna = atualiza_pos(inicio, ponteiro, linha, coluna)
                continue

        # 2. Comentário de linha //
        if codigo_fonte.startswith("//", ponteiro):
            inicio = ponteiro
            while ponteiro < tamanho_codigo and codigo_fonte[ponteiro] != "\n":
                ponteiro += 1
            linha, coluna = atualiza_pos(inicio, ponteiro, linha, coluna)
            continue

        # 3. Comentário de bloco /*
        if codigo_fonte.startswith("/*", ponteiro):
            inicio = ponteiro
            ponteiro += 2
            while ponteiro < tamanho_codigo and not codigo_fonte.startswith("*/", ponteiro):
                ponteiro += 1

            if ponteiro < tamanho_codigo and codigo_fonte.startswith("*/", ponteiro):
                ponteiro += 2
                linha, coluna = atualiza_pos(inicio, ponteiro, linha, coluna)
                continue
            else:
                print(f"Erro léxico: comentário de bloco não fechado @ {linha_tok}:{coluna_tok}")
                lexema = "/*...EOF"
                linha_tok = linha
                coluna_tok = coluna
                lista_tokens.append(Token("ERROR", lexema, linha_tok, coluna_tok))
                break

        # 4. Identificador ou palavra reservada
        if caractere_atual.isalpha() or caractere_atual == "_":
            inicio = ponteiro
            linha_tok = linha
            coluna_tok = coluna
            lexema = ""
            while (
                ponteiro < tamanho_codigo
                and (codigo_fonte[ponteiro].isalnum() or codigo_fonte[ponteiro] == "_")
            ):
                lexema += codigo_fonte[ponteiro]
                ponteiro += 1

            if lexema in palavras_reservadas:
                token_tipo = palavras_reservadas[lexema]
            else:
                token_tipo = "ID"
                tabela_simbolos[lexema] = tabela_simbolos.get(lexema, 0) + 1

            linha, coluna = atualiza_pos(inicio, ponteiro, linha, coluna)
            lista_tokens.append(Token(token_tipo, lexema, linha_tok, coluna_tok))
            continue

        # 4a. String: "texto\n"
        if caractere_atual == '"':
            inicio = ponteiro
            linha_tok = linha
            coluna_tok = coluna

            ponteiro += 1
            lexema = '"'
            fechado = False
            while ponteiro < tamanho_codigo:
                ch = codigo_fonte[ponteiro]
                lexema += ch
                ponteiro += 1
                if ch == "\\":
                    if ponteiro < tamanho_codigo:
                        lexema += codigo_fonte[ponteiro]
                        ponteiro += 1
                elif ch == '"':
                    fechado = True
                    break
                elif ch == "\n":
                    break
            linha, coluna = atualiza_pos(inicio, ponteiro, linha, coluna)
            if fechado:
                lista_tokens.append(Token("TEXTO", lexema, linha_tok, coluna_tok))
            else:
                print(f"Erro léxico: string não terminada @ linha {linha_tok}, coluna {coluna_tok}")
                print(f"Lexema de erro: {repr(lexema)}")
                lista_tokens.append(Token("ERROR", lexema, linha_tok, coluna_tok))
            continue

        # 4b. Char: 'a' ou '\n'
        if caractere_atual == "'":
            inicio = ponteiro
            linha_tok = linha
            coluna_tok = coluna

            ponteiro += 1
            lexema = "'"
            fechado = False
            if ponteiro < tamanho_codigo:
                ch = codigo_fonte[ponteiro]
                lexema += ch
                ponteiro += 1
                if ch == "\\":
                    if ponteiro < tamanho_codigo:
                        lexema += codigo_fonte[ponteiro]
                        ponteiro += 1
            if ponteiro < tamanho_codigo and codigo_fonte[ponteiro] == "'":
                lexema += "'"
                ponteiro += 1
                fechado = True

            linha, coluna = atualiza_pos(inicio, ponteiro, linha, coluna)
            if fechado:
                lista_tokens.append(Token("CHAR_LITERAL", lexema, linha_tok, coluna_tok))
            else:
                print(f"Erro léxico: literal de caractere não terminado @ {linha_tok}:{coluna_tok}")
                print(f"Lexema de erro: {repr(lexema)}")
                lista_tokens.append(Token("ERROR", lexema, linha_tok, coluna_tok))
            continue

        # 5. Número
        if caractere_atual.isdigit():
            inicio = ponteiro
            linha_tok = linha
            coluna_tok = coluna

            lexema = ""
            is_float = False

            while ponteiro < tamanho_codigo and codigo_fonte[ponteiro].isdigit():
                lexema += codigo_fonte[ponteiro]
                ponteiro += 1

            # vírgula como decimal -> erro
            if (
                ponteiro + 1 < tamanho_codigo
                and codigo_fonte[ponteiro] == ","
                and codigo_fonte[ponteiro + 1].isdigit()
            ):
                err_inicio = inicio
                err_lex = lexema + ","
                ponteiro += 1
                while (
                    ponteiro < tamanho_codigo
                    and codigo_fonte[ponteiro].isdigit()
                ):
                    err_lex += codigo_fonte[ponteiro]
                    ponteiro += 1
                linha, coluna = atualiza_pos(err_inicio, ponteiro, linha, coluna)
                print(f"Erro léxico: uso de vírgula como separador decimal (3,14) @ {linha_tok}:{coluna_tok}")
                print(f"Lexema de erro: {repr(err_lex)}")
                lista_tokens.append(Token("ERROR", err_lex, linha_tok, coluna_tok))
                continue

            # ponto decimal (float)
            if ponteiro < tamanho_codigo and codigo_fonte[ponteiro] == ".":
                is_float = True
                lexema += "."
                ponteiro += 1
                if ponteiro < tamanho_codigo and codigo_fonte[ponteiro].isdigit():
                    while (
                        ponteiro < tamanho_codigo
                        and codigo_fonte[ponteiro].isdigit()
                    ):
                        lexema += codigo_fonte[ponteiro]
                        ponteiro += 1

            # identificador começando por número -> erro
            if (
                ponteiro < tamanho_codigo
                and (codigo_fonte[ponteiro].isalpha() or codigo_fonte[ponteiro] == "_")
            ):
                while (
                    ponteiro < tamanho_codigo
                    and (codigo_fonte[ponteiro].isalnum() or codigo_fonte[ponteiro] == "_")
                ):
                    lexema += codigo_fonte[ponteiro]
                    ponteiro += 1
                linha, coluna = atualiza_pos(inicio, ponteiro, linha, coluna)
                print(f"Erro léxico: identificador não pode começar com número @ {linha_tok}:{coluna_tok}")
                print(f"Lexema de erro: {repr(lexema)}")
                lista_tokens.append(Token("ERROR", lexema, linha_tok, coluna_tok))
            else:
                linha, coluna = atualiza_pos(inicio, ponteiro, linha, coluna)
                atributo = float(lexema) if is_float else int(lexema)
                lista_tokens.append(Token("NUM", lexema, linha_tok, coluna_tok, atributo))
            continue

        # 6. Operador de 3 caracteres: ...
        if (
            ponteiro + 2 < tamanho_codigo
            and codigo_fonte[ponteiro : ponteiro + 3] == "..."
        ):
            inicio = ponteiro
            linha_tok = linha
            coluna_tok = coluna
            ponteiro += 3
            linha, coluna = atualiza_pos(inicio, ponteiro, linha, coluna)
            lista_tokens.append(Token("ELLIPSIS", "...", linha_tok, coluna_tok))
            continue

        # 7. Operadores de 2 caracteres
        if (
            ponteiro + 1 < tamanho_codigo
            and codigo_fonte[ponteiro : ponteiro + 2] in mapa2
        ):
            inicio = ponteiro
            linha_tok = linha
            coluna_tok = coluna
            op = codigo_fonte[ponteiro : ponteiro + 2]
            tipo = mapa2[op]
            ponteiro += 2
            linha, coluna = atualiza_pos(inicio, ponteiro, linha, coluna)
            lista_tokens.append(Token(tipo, op, linha_tok, coluna_tok))
            continue

        # 8. Operadores/delimitadores 1 caractere
        if caractere_atual in mapa:
            inicio = ponteiro
            linha_tok = linha
            coluna_tok = coluna
            ponteiro += 1
            linha, coluna = atualiza_pos(inicio, ponteiro, linha, coluna)
            lista_tokens.append(Token(mapa[caractere_atual], caractere_atual, linha_tok, coluna_tok))
            continue

        # 9. Erro léxico genérico
        print(f"Erro léxico: caractere inválido '{caractere_atual}' @ {linha_tok}:{coluna_tok}")
        print(f"Lexema de erro: {repr(caractere_atual)}")
        inicio = ponteiro
        linha_tok = linha
        coluna_tok = coluna
        ponteiro += 1
        linha, coluna = atualiza_pos(inicio, ponteiro, linha, coluna)
        lista_tokens.append(Token("ERROR", caractere_atual, linha_tok, coluna_tok))

    # Token de fim de arquivo (útil pro parser)
    lista_tokens.append(Token("EOF", "", linha, coluna))

    return lista_tokens, tabela_simbolos


def categoria_do_token(tok: Token) -> str:
    if tok.lexema in palavras_reservadas:
        return "Palavra reservada"

    if tok.tipo == "NUM":
        return "Número decimal" if "." in tok.lexema else "Número inteiro"

    return categorias.get(tok.tipo, "Outro")


def imprimir_tokens(lista_tokens):
    if not lista_tokens:
        print("Nenhum token encontrado.")
        return
    rows = [
        [t.tipo, categoria_do_token(t), t.lexema, t.atributo, t.linha, t.coluna]
        for t in lista_tokens
    ]
    print(
        tabulate(
            rows,
            headers=["Token", "Categoria", "Lexema", "Atributo", "Linha", "Coluna"],
            tablefmt="github",
        )
    )


def imprimir_simbolos(tabela_simbolos):
    if not tabela_simbolos:
        print("Nenhum identificador encontrado na tabela de símbolos.")
        return
    rows = [[k, v] for k, v in sorted(tabela_simbolos.items())]
    print(tabulate(rows, headers=["ID", "Ocorrências"], tablefmt="github"))