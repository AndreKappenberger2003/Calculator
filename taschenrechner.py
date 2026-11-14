import ast
import math
import operator
import tkinter as tk

BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}
UN_OPS = {ast.USub: operator.neg, ast.UAdd: operator.pos}
FUNKTIONEN = {"sqrt": math.sqrt, "exp": math.exp}
KONSTANTEN = {"e": math.e, "pi": math.pi}


def berechne(ausdruck: str):
    """Wertet einen mathematischen Ausdruck sicher aus (ohne eval)."""

    def _eval(k):
        if isinstance(k, ast.Expression):
            return _eval(k.body)
        if isinstance(k, ast.Constant) and isinstance(k.value, (int, float)):
            return k.value
        if isinstance(k, ast.Name) and k.id in KONSTANTEN:
            return KONSTANTEN[k.id]
        if isinstance(k, ast.BinOp) and type(k.op) in BIN_OPS:
            links, rechts = _eval(k.left), _eval(k.right)
            if isinstance(k.op, ast.Pow) and abs(rechts) > 10000:
                raise ValueError("Exponent zu groß")
            return BIN_OPS[type(k.op)](links, rechts)
        if isinstance(k, ast.UnaryOp) and type(k.op) in UN_OPS:
            return UN_OPS[type(k.op)](_eval(k.operand))
        if (
            isinstance(k, ast.Call)
            and isinstance(k.func, ast.Name)
            and k.func.id in FUNKTIONEN
            and len(k.args) == 1
            and not k.keywords
        ):
            return FUNKTIONEN[k.func.id](_eval(k.args[0]))
        raise ValueError("Ungültiger Ausdruck")

    return _eval(ast.parse(ausdruck, mode="eval"))


# Taste -> Token, das in den Ausdruck eingefügt wird
EINFUEGEN = {
    "√": "sqrt(",
    "eˣ": "exp(",
    "xʸ": "**",
    "x²": "**2",
    "π": "pi",
}
# Token -> Darstellung im Display
ANZEIGE = {"sqrt(": "√(", "exp(": "e^(", "**": "^", "**2": "²", "pi": "π", "*": "×", "/": "÷"}


class Taschenrechner(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Taschenrechner")
        self.resizable(False, False)
        self.configure(bg="#1e1e1e")

        self.tokens = []
        self.anzeige_var = tk.StringVar(value="0")

        anzeige = tk.Entry(
            self,
            textvariable=self.anzeige_var,
            font=("Segoe UI", 26),
            justify="right",
            bd=0,
            bg="#2b2b2b",
            fg="white",
            readonlybackground="#2b2b2b",
            state="readonly",
        )
        anzeige.grid(row=0, column=0, columnspan=5, sticky="nsew", padx=10, pady=10, ipady=12)

        # (Text, Zeile, Spalte, Zeilen, Spalten)
        tasten = [
            ("C", 1, 0, 1, 1), ("⌫", 1, 1, 1, 1), ("(", 1, 2, 1, 1), (")", 1, 3, 1, 1), ("/", 1, 4, 1, 1),
            ("√", 2, 0, 1, 1), ("eˣ", 2, 1, 1, 1), ("xʸ", 2, 2, 1, 1), ("π", 2, 3, 1, 1), ("*", 2, 4, 1, 1),
            ("7", 3, 0, 1, 1), ("8", 3, 1, 1, 1), ("9", 3, 2, 1, 1), ("e", 3, 3, 1, 1), ("-", 3, 4, 1, 1),
            ("4", 4, 0, 1, 1), ("5", 4, 1, 1, 1), ("6", 4, 2, 1, 1), ("%", 4, 3, 1, 1), ("+", 4, 4, 1, 1),
            ("1", 5, 0, 1, 1), ("2", 5, 1, 1, 1), ("3", 5, 2, 1, 1), ("±", 5, 3, 1, 1), ("=", 5, 4, 2, 1),
            ("0", 6, 0, 1, 2), (".", 6, 2, 1, 1), ("x²", 6, 3, 1, 1),
        ]

        for text, z, s, zs, ss in tasten:
            if text in ("=", "/", "*", "-", "+"):
                farbe = "#ff9500"
            elif text in ("C", "⌫", "(", ")", "%", "±", "√", "eˣ", "xʸ", "x²", "π", "e"):
                farbe = "#505050"
            else:
                farbe = "#333333"

            tk.Button(
                self,
                text=text,
                font=("Segoe UI", 16),
                width=4,
                height=2,
                bd=0,
                bg=farbe,
                fg="white",
                activebackground="#707070",
                activeforeground="white",
                command=lambda t=text: self.taste(t),
            ).grid(row=z, column=s, rowspan=zs, columnspan=ss, padx=3, pady=3, sticky="nsew")

        self.bind("<Key>", self.tastatur)
        self.bind("<Return>", lambda e: self.taste("="))
        self.bind("<BackSpace>", lambda e: self.taste("⌫"))
        self.bind("<Escape>", lambda e: self.taste("C"))

    # ---------- Anzeige ----------
    def aktualisiere(self):
        text = "".join(ANZEIGE.get(t, t) for t in self.tokens)
        self.anzeige_var.set(text if text else "0")

    def fehler(self, meldung="Fehler"):
        self.tokens = []
        self.anzeige_var.set(meldung)

    # ---------- Tasten ----------
    def taste(self, t):
        if t == "C":
            self.tokens = []
        elif t == "⌫":
            if self.tokens:
                self.tokens.pop()
        elif t == "=":
            self.ergebnis()
            return
        elif t == "±":
            if self.tokens[:2] == ["-", "("] and self.tokens[-1:] == [")"]:
                self.tokens = self.tokens[2:-1]
            elif self.tokens:
                self.tokens = ["-", "("] + self.tokens + [")"]
        elif t == "%":
            try:
                self.tokens = [self.format(berechne("".join(self.tokens)) / 100)]
            except Exception:
                self.fehler()
                return
        else:
            self.tokens.append(EINFUEGEN.get(t, t))
        self.aktualisiere()

    @staticmethod
    def format(wert):
        if isinstance(wert, float):
            wert = round(wert, 12)
            if wert.is_integer():
                wert = int(wert)
        return str(wert)

    def ergebnis(self):
        if not self.tokens:
            return
        try:
            wert = berechne("".join(self.tokens))
            self.tokens = [self.format(wert)]
            self.aktualisiere()
        except ZeroDivisionError:
            self.fehler("Teilen durch 0")
        except (ValueError, OverflowError):
            self.fehler("Ungültig / zu groß")
        except Exception:
            self.fehler()

    def tastatur(self, event):
        if event.char and event.char in "0123456789.+-*/%()e":
            self.taste(event.char)
        elif event.char == "^":
            self.taste("xʸ")


if __name__ == "__main__":
    Taschenrechner().mainloop()
