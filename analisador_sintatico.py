from __future__ import annotations
from dataclasses import dataclass, is_dataclass
from typing import List, Optional, Any, Tuple, Dict
import os

# IMPORTA o léxico
#from analisador_lexico import analisar_lexema, Token as LexToken

# TOKENS usados pelo parser
@dataclass
class Token:
    type: str
    lex: str
    line: int
    col: int
    attr: Any = None


def tokens_from_lexer(lista_lex) -> List[Token]:
    """
    Converte a lista de tokens do analisador léxico
    para o formato esperado pelo Parser (Token).
    NÃO chama o analisador léxico de novo.
    """
    tokens_parser: List[Token] = []
    for t in lista_lex:
        tokens_parser.append(
            Token(
                type=t.tipo,
                lex=t.lexema,
                line=t.linha,
                col=t.coluna,
                attr=t.atributo,
            )
        )
    return tokens_parser


# -----------------------------------------------
# Visualizador de AST genérico (gera PNG)
# -----------------------------------------------
try:
    import matplotlib.pyplot as plt
    HAVE_MPL = True
except Exception:
    HAVE_MPL = False

NodeLike = Any


def node_label(n: NodeLike) -> str:
    tname = type(n).__name__

    if tname == "Program":
        return "Program"
    if tname == "FuncDef":
        return f"Func({getattr(n, 'name', '?')})"
    if tname == "VarDecl":
        return f"Decl({getattr(n, 'vartype', '?')})"
    if tname == "Assign":
        return "Assign"
    if tname == "If":
        return "If"
    if tname == "While":
        return "While"
    if tname == "Return":
        return "Return"
    if tname == "Block":
        return "Block"
    if tname == "Call":
        return "Call"
    if tname == "Index":
        return "Index"
    if tname == "BinOp":
        return f"BinOp('{getattr(n, 'op', '?')}')"
    if tname == "Var":
        return f"Id({getattr(n, 'name', '?')})"
    if tname == "Num":
        return f"Num({getattr(n, 'value', '?')})"
    if tname == "TextLit":
        return "Text"
    if tname == "CharLit":
        return "Char"
    return tname


# ----------------------------------------
# Lista de filhos
# ----------------------------------------

def children(n: NodeLike) -> List[NodeLike]:
    tname = type(n).__name__
    # Mapeamento pelos atributos usados na sua AST

    if tname == "Program":
        return list(getattr(n, "body", []))
    if tname == "FuncDef":
        # primeiro parâmetros, depois corpo
        return list(getattr(n, "params", [])) + [getattr(n, "body", None)]
    if tname == "VarDecl":
        return [getattr(n, "name", None), getattr(n, "init", None)]
    if tname == "Assign":
        return [getattr(n, "target", None), getattr(n, "value", None)]
    if tname == "If":
        lst = [getattr(n, "test", None), getattr(n, "then", None)]
        other = getattr(n, "otherwise", None)
        if other is not None:
            lst.append(other)
        return lst
    if tname == "While":
        return [getattr(n, "test", None), getattr(n, "body", None)]
    if tname == "Return":
        v = getattr(n, "value", None)
        return [v] if v is not None else []
    if tname == "Block":
        return list(getattr(n, "body", []))
    if tname == "Call":
        return [getattr(n, "callee", None)] + list(getattr(n, "args", []))
    if tname == "Index":
        return [getattr(n, "target", None), getattr(n, "index", None)]
    if tname == "BinOp":
        return [getattr(n, "left", None), getattr(n, "right", None)]

    # fallback genérico para dataclasses
    if is_dataclass(n):
        out: List[Any] = []
        for k, v in n.__dict__.items():
            if k in ("line", "col", "op", "name", "value"):
                continue
            if isinstance(v, list):
                out.extend(v)
            elif v is not None:
                out.append(v)
        return out
    if hasattr(n, "children"):
        return list(getattr(n, "children"))
    return []


# -------------------------------------------------
# Layout recursivo (retorna posicoes e largura)
# -------------------------------------------------

def _compute_layout(
    n: NodeLike, x0=0.0, y0=0.0, y_spacing=1.6
) -> Tuple[Dict[int, Tuple[float, float]], float]:
    ch = [c for c in children(n) if c is not None]
    if not ch:
        return ({id(n): (x0, y0)}, 1.0)

    pos: Dict[int, Tuple[float, float]] = {}
    widths: List[float] = []
    subs: List[NodeLike] = []

    for c in ch:
        subpos, w = _compute_layout(c, 0, 0, y_spacing)
        pos.update(subpos)
        widths.append(w)
        subs.append(c)

    total_w = sum(widths) + (len(widths) - 1) * 0.8
    cur_x = x0 - total_w / 2.0

    def shift(node: NodeLike, dx: float, dy: float):
        x, y = pos[id(node)]
        pos[id(node)] = (x + dx, y + dy)
        for cc in children(node):
            if cc is not None:
                shift(cc, dx, dy)

    for c, w in zip(subs, widths):
        cx = cur_x + w / 2.0
        shift(c, cx, y0 - y_spacing)
        cur_x += w + 0.8

    pos[id(n)] = (x0, y0)
    return pos, total_w


# -----------------------------------------
# Função principal: salva a árvore em PNG
# -----------------------------------------

def draw_tree(root: NodeLike, filename: str, figsize=(10, 7), dpi: int = 160):
    pos, _ = _compute_layout(root, 0.0, 0.0)

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_axis_off()

    def draw_edges(node: NodeLike):
        x, y = pos[id(node)]
        for c in children(node):
            if c is None:
                continue
            xc, yc = pos[id(c)]
            ax.plot([x, xc], [y - 0.05, yc + 0.05])
            draw_edges(c)

    def draw_nodes(node: NodeLike):
        x, y = pos[id(node)]
        bbox = dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1)
        ax.text(
            x,
            y,
            node_label(node),
            ha="center",
            va="center",
            bbox=bbox,
            fontsize=10,
        )
        for c in children(node):
            if c is not None:
                draw_nodes(c)

    draw_edges(root)
    draw_nodes(root)

    xs = [xy[0] for xy in pos.values()]
    ys = [xy[1] for xy in pos.values()]
    pad = 1.2
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - pad, max(ys) + pad)
    plt.tight_layout()
    plt.savefig(filename, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


# ----------------- AST para mini-C -----------------
@dataclass
class Program:
    body: List[Any]

@dataclass
class Block:
    body: List[Any]
    line: int
    col: int

@dataclass
class VarDecl:
    vartype: str
    name: "Var"
    init: Optional[Any]
    line: int
    col: int

@dataclass
class FuncDef:
    rettype: str            # "int", "void", ...
    name: str               # "main", ...
    params: List["VarDecl"] # parâmetros como declarações simples
    body: Block             # corpo da função
    line: int
    col: int

@dataclass
class Assign:
    target: "Var"
    value: Any
    line: int
    col: int

@dataclass
class If:
    test: Any
    then: Block | Any
    otherwise: Optional[Block | Any]
    line: int
    col: int

@dataclass
class While:
    test: Any
    body: Block | Any
    line: int
    col: int

@dataclass
class Return:
    value: Optional[Any]
    line: int
    col: int

@dataclass
class Call:
    callee: Any
    args: List[Any]
    line: int
    col: int

@dataclass
class Index:
    target: Any
    index: Any
    line: int
    col: int

@dataclass
class BinOp:
    left: Any
    op: str
    right: Any
    line: int
    col: int

@dataclass
class Var:
    name: str
    line: int
    col: int

@dataclass
class Num:
    value: float
    line: int
    col: int

@dataclass
class TextLit:
    value: str
    line: int
    col: int

@dataclass
class CharLit:
    value: str
    line: int
    col: int

# Conjunto de sincronização (recuperação de erros)
SYNC_SET = {"SEMI", "RBRACE", "EOF"}


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0
        self.errors: List[str] = []
        self.in_panic = False

    # ---------- utilidades de fluxo ----------
    def cur(self) -> Token:
        return self.tokens[self.i]

    def peek(self, k: int = 1) -> Token:
        j = self.i + k
        if j < len(self.tokens):
            return self.tokens[j]
        return self.tokens[-1]

    def match(self, *types: str) -> Optional[Token]:
        if self.cur().type in types:
            t = self.cur()
            self.i += 1
            return t
        return None

    def consume(self, typ: str) -> Optional[Token]:
        if self.cur().type == typ:
            t = self.cur()
            self.i += 1
            return t
        return None

    # ---------- erros ----------
    def found_lex(self, t: Token) -> str:
        if t.type == "EOF":
            return ""
        return t.lex

    def report(self, msg: str, t: Optional[Token] = None):
        if t is None:
            t = self.cur()
        self.errors.append(
            f"  - {msg} (encontrado '{self.found_lex(t)}') @ {t.line}:{t.col}"
        )

    def human_token(self, typ: str) -> str:
        mapping = {
            "NUM": "número",
            "ID": "identificador",
            "LPAREN": "'('",
            "RPAREN": "')'",
            "LBRACE": "'{'",
            "RBRACE": "'}'",
            "LBRACK": "'['",
            "RBRACK": "']'",
            "SEMI": "';'",
            "COMMA": "','",
            "EQUAL": "'='",
        }
        return mapping.get(typ, typ)

    def expect(self, typ: str, msg_when_fail: Optional[str] = None) -> Optional[Token]:
        if self.cur().type == typ:
            t = self.cur()
            self.i += 1
            return t
        msg = (
            msg_when_fail
            if msg_when_fail is not None
            else f"Esperado '{self.human_token(typ)}'"
        )
        self.report(msg, self.cur())
        self.synchronize()
        return None

    def expect_any(
        self, types: List[str], human_msg_list: Optional[str] = None
    ) -> Optional[Token]:
        if self.cur().type in types:
            t = self.cur()
            self.i += 1
            return t
        if human_msg_list is None:
            human_msg_list = ", ".join([self.human_token(t) for t in types])
        self.report(f"Esperado {human_msg_list}", self.cur())
        self.synchronize()
        return None

    def synchronize(self):

        # modo pânico: avança até um sincronizador; se estiver em ';' ou '}', consome
        while self.cur().type not in SYNC_SET:
            self.i += 1
        # Consome ; ou } para não travar antes do EOL
        if self.cur().type in {"SEMI", "RBRACE"}:
            self.i += 1

    # ---------- entrada principal ----------
    def parse_program(self) -> Tuple[Program, List[str]]:
        """
        Program ::= (Stmt (';' Stmt)*)* EOF
        (na prática: vamos lendo Stmt até EOF,
        consumindo ';' quando existir)
        """
        body: List[Any] = []
        while self.cur().type != "EOF":

            # Ignora diretivas de pré-processamento no topo
            if self.cur().type == "PP_DIRECTIVE":
                self.i += 1
                continue

            s = self.parse_top_level()
            if s is not None:
                body.append(s)

            # consome ';' opcional entre statements
            self.match("SEMI")

        return Program(body), self.errors
    
    # ------------ Decide entre função e declaração global --------
    def parse_top_level(self) -> Optional[Any]:
        """
        Nível de arquivo (top-level):

        - FuncDef: tipo ID '(' ... ')' Block
        - Declaração global de variável: tipo ID [= E] ';'
        - (ou um statement solto, se quiser permitir)
        """

        # Padrão de função: <tipo> <id> '('
        if (self.cur().type in {"INT", "FLOAT", "CHAR", "DOUBLE", "STRING", "VOID"}
                and self.peek().type == "ID"
                and self.peek(2).type == "LPAREN"):
            return self.parse_funcdef()

        # Senão, trata como declaração/statement normal
        return self.parse_stmt()

    # ---------- statements ----------
    def parse_stmt(self) -> Optional[Any]:
        t = self.cur()

        # Ignora diretivas de pré-processamento (#include etc.)
        if t.type == "PP_DIRECTIVE":
            self.i += 1
            return None

        # Declaração de variável
        if t.type in {"INT", "FLOAT", "CHAR", "DOUBLE", "STRING", "VOID"}:
            return self.parse_vardecl()
        if t.type == "IF":
            return self.parse_if()
        if t.type == "WHILE":
            return self.parse_while()
        if t.type == "RETURN":
            return self.parse_return()

        # Atribuição: ID '=' E
        if t.type == "ID" and self.peek().type == "EQUAL":
            idtok = self.consume("ID")
            self.expect("EQUAL", "Esperado '='")
            value = self.parse_E()
            if idtok is None:
                return None
            return Assign(
                Var(idtok.lex, idtok.line, idtok.col),
                value,
                idtok.line,
                idtok.col,
            )

        # Caso geral: expressão como statement
        return self.parse_E()
    
    def parse_funcdef(self) -> Optional[FuncDef]:
        # tipo de retorno
        type_tok = self.cur()
        self.i += 1

        # nome da função
        idtok = self.expect("ID", "Esperado identificador de função")

        # '('
        self.expect("LPAREN", "Esperado '(' após nome da função")

        params: List[VarDecl] = []

        # parâmetros
        if self.cur().type != "RPAREN":
            # CASO ESPECIAL: 'void)' => nenhum parâmetro
            if self.cur().type == "VOID" and self.peek().type == "RPAREN":
                self.i += 1  # consome o VOID e não cria parâmetro
            else:
                while True:
                    if self.cur().type not in {"INT", "FLOAT", "CHAR", "DOUBLE", "STRING", "VOID"}:
                        self.report("Esperado tipo de parâmetro", self.cur())
                        self.synchronize()
                        break

                    p_type_tok = self.cur()
                    self.i += 1
                    p_idtok = self.expect("ID", "Esperado identificador de parâmetro")

                    if p_idtok is not None:
                        params.append(
                            VarDecl(
                                vartype=p_type_tok.lex,
                                name=Var(p_idtok.lex, p_idtok.line, p_idtok.col),
                                init=None,
                                line=p_type_tok.line,
                                col=p_type_tok.col,
                            )
                        )

                    if not self.match("COMMA"):
                        break

        self.expect("RPAREN", "Esperado ')' após parâmetros")

        body = self.parse_block()

        if idtok is None:
            return None

        return FuncDef(
            rettype=type_tok.lex,
            name=idtok.lex,
            params=params,
            body=body,
            line=type_tok.line,
            col=type_tok.col,
        )



    def parse_vardecl(self) -> Optional[VarDecl]:
        type_tok = self.cur()
        if type_tok.type not in {"INT", "FLOAT", "CHAR", "DOUBLE", "STRING", "VOID"}:
            self.report("Esperado tipo (int, float, char, ...)", type_tok)
            self.synchronize()
            return None

        self.i += 1  # consome o tipo

        idtok = self.expect("ID", "Esperado identificador")

        init = None
        if self.match("EQUAL"):
            init = self.parse_E()

        if idtok is None:
            return None

        vartype_lex = type_tok.lex
        return VarDecl(
            vartype=vartype_lex,
            name=Var(idtok.lex, idtok.line, idtok.col),
            init=init,
            line=type_tok.line,
            col=type_tok.col,
        )

    def parse_if(self) -> Optional[If]:
        iftok = self.expect("IF")
        self.expect("LPAREN", "Esperado '('")
        test = self.parse_E()
        self.expect("RPAREN", "Esperado ')'")
        then = self.parse_block()
        otherwise = None
        if self.match("ELSE"):
            otherwise = self.parse_block()
        if iftok is None:
            return None
        return If(test, then, otherwise, iftok.line, iftok.col)

    def parse_while(self) -> Optional[While]:
        wt = self.expect("WHILE")
        self.expect("LPAREN", "Esperado '('")
        test = self.parse_E()
        self.expect("RPAREN", "Esperado ')'")
        body = self.parse_block()
        if wt is None:
            return None
        return While(test, body, wt.line, wt.col)

    def parse_return(self) -> Optional[Return]:
        rt = self.expect("RETURN")
        # Return E?
        if self.cur().type in {"SEMI", "RBRACE", "EOF"}:
            return Return(None, rt.line if rt else 0, rt.col if rt else 0)
        val = self.parse_E()
        return Return(val, rt.line if rt else 0, rt.col if rt else 0)

    def parse_block(self) -> Any:
        # Block ::= '{' StmtList? '}' | Stmt
        if self.match("LBRACE"):
            stmts: List[Any] = []
            while self.cur().type not in {"RBRACE", "EOF"}:
                s = self.parse_stmt()
                if s is not None:
                    stmts.append(s)
                self.match("SEMI")
            rb = self.expect("RBRACE", "Esperado '}'")
            line = rb.line if rb else (stmts[0].line if stmts else 0)
            col = rb.col if rb else (stmts[0].col if stmts else 0)
            return Block(stmts, line, col)
        # Sem chaves: um único statement
        s = self.parse_stmt()
        return s

    # ---------- expressões ----------
    def parse_E(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.match("OR"):
            op = "||"
            right = self.parse_and()
            left = BinOp(
                left,
                op,
                right,
                left.line if hasattr(left, "line") else self.cur().line,
                getattr(left, "col", self.cur().col),
            )
        return left

    def parse_and(self):
        left = self.parse_equality()
        while self.match("AND"):
            op = "&&"
            right = self.parse_equality()
            left = BinOp(
                left,
                op,
                right,
                left.line if hasattr(left, "line") else self.cur().line,
                getattr(left, "col", self.cur().col),
            )
        return left

    def parse_equality(self):
        left = self.parse_rel()
        while self.cur().type in {"EQ", "NE"}:
            if self.match("EQ"):
                op = "=="
            else:
                self.consume("NE")
                op = "!="
            right = self.parse_rel()
            left = BinOp(
                left,
                op,
                right,
                left.line if hasattr(left, "line") else self.cur().line,
                getattr(left, "col", self.cur().col),
            )
        return left

    def parse_rel(self):
        left = self.parse_add()
        while self.cur().type in {"LT", "LE", "GT", "GE"}:
            if self.match("LT"):
                op = "<"
            elif self.match("LE"):
                op = "<="
            elif self.match("GT"):
                op = ">"
            else:
                self.consume("GE")
                op = ">="
            right = self.parse_add()
            left = BinOp(
                left,
                op,
                right,
                left.line if hasattr(left, "line") else self.cur().line,
                getattr(left, "col", self.cur().col),
            )
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.cur().type in {"PLUS", "MINUS"}:
            if self.match("PLUS"):
                op = "+"
            else:
                self.consume("MINUS")
                op = "-"
            right = self.parse_mul()
            left = BinOp(
                left,
                op,
                right,
                left.line if hasattr(left, "line") else self.cur().line,
                getattr(left, "col", self.cur().col),
            )
        return left

    def parse_mul(self):
        left = self.parse_postfix()
        while self.cur().type in {"TIMES", "DIVIDE", "MOD"}:
            if self.match("TIMES"):
                op = "*"
            elif self.match("DIVIDE"):
                op = "/"
            else:
                self.consume("MOD")
                op = "%"
            right = self.parse_postfix()
            left = BinOp(
                left,
                op,
                right,
                left.line if hasattr(left, "line") else self.cur().line,
                getattr(left, "col", self.cur().col),
            )
        return left

    def parse_postfix(self):
        node = self.parse_primary()

        # Pós-fixos encadeáveis: chamada e indexação
        while True:
            if self.match("LPAREN"):
                args: List[Any] = []
                if self.cur().type != "RPAREN":
                    args.append(self.parse_E())
                    while self.match("COMMA"):
                        args.append(self.parse_E())
                rp = self.expect("RPAREN", "Esperado ')'")
                line = node.line if hasattr(node, "line") else (rp.line if rp else 0)
                col = node.col if hasattr(node, "col") else (rp.col if rp else 0)
                node = Call(node, args, line, col)
                continue
            if self.match("LBRACK"):
                idx = self.parse_E()
                rb = self.expect("RBRACK", "Esperado ']'")
                line = node.line if hasattr(node, "line") else (rb.line if rb else 0)
                col = node.col if hasattr(node, "col") else (rb.col if rb else 0)
                node = Index(node, idx, line, col)
                continue
            break
        return node

    def parse_primary(self):
        t = self.cur()
        if self.match("NUM"):
            return Num(float(t.lex), t.line, t.col)
        if self.match("TEXTO"):
            return TextLit(t.lex, t.line, t.col)
        if self.match("CHAR_LITERAL"):
            return CharLit(t.lex, t.line, t.col)
        if self.match("ID"):
            return Var(t.lex, t.line, t.col)
        if self.match("LPAREN"):
            e = self.parse_E()
            self.expect("RPAREN", "Esperado ')'")
            return e
        
        # Falhou: mensagem padrão pedida
        self.report(
            "Esperado número, identificador, string, char ou '('", t
        )
        self.synchronize()
        # retorna um nó fictício para seguir
        return Num(0.0, t.line, t.col)
