import os
from analisador_sintatico import Parser, tokens_from_lexer, draw_tree, HAVE_MPL
from analisador_lexico import analisar_lexema, imprimir_tokens, imprimir_simbolos

EXEMPLOS_DIR = "exemplos"
TREES_DIR = "trees"


def processar_arquivo(nome_arquivo: str):
    caminho = os.path.join(EXEMPLOS_DIR, nome_arquivo)
    with open(caminho, encoding="utf-8") as f:
        codigo = f.read()

    print("\n" + "=" * 80)
    print(f"Analisando arquivo: {caminho}")

    # --- 1) Análise léxica ---
    lista_tokens, tabela_simbolos = analisar_lexema(codigo)

    print("\nTokens encontrados:")
    imprimir_tokens(lista_tokens)

    print("\nTabela de símbolos:")
    imprimir_simbolos(tabela_simbolos)

    # --- converte tokens léxicos -> tokens do parser (sem rodar léxico de novo) ---
    tokens = tokens_from_lexer(lista_tokens)

    # --- 2) Análise sintática ---
    parser = Parser(tokens)
    program, errors = parser.parse_program()

    if errors:
        print("\nErros sintáticos encontrados:")
        for e in errors:
            print(e)
    else:
        print("\nParse OK, AST construída!")
        if HAVE_MPL:
            os.makedirs(TREES_DIR, exist_ok=True)
            base, _ = os.path.splitext(nome_arquivo)
            out_png = os.path.join(TREES_DIR, f"{base}.png")
            draw_tree(program, out_png)
            print(f"AST salva em {out_png}")
        else:
            print("matplotlib não encontrado — AST não salva em PNG.")


if __name__ == "__main__":
    arquivos = [
        f for f in os.listdir(EXEMPLOS_DIR)
        if f.lower().endswith(".c")
    ]
    if not arquivos:
        print("Nenhum arquivo .c encontrado em 'exemplos/'.")
    else:
        for nome in sorted(arquivos):
            processar_arquivo(nome)