# compiler/cli.py
import argparse, pathlib, json, shutil, importlib.resources as pkg
import antlr4

from .fcdl.FCDLLexer  import FCDLLexer
from .fcdl.FCDLParser import FCDLParser
from .visitor         import BuildIRVisitor
from .planner         import plan
from . import generator   # generator package (template copying helpers)

import dataclasses, json
from compiler.generator import render

"""
def encode(obj):
    # any dataclass (Module, Layer, …) ➜ plain dict
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    # otherwise let json decide or raise
    raise TypeError(f"{obj} is not JSON serialisable")
"""

def parse_file(path):
    stream = antlr4.FileStream(str(path), encoding="utf-8")
    lexer  = FCDLLexer(stream)
    tokens = antlr4.CommonTokenStream(lexer)
    tree   = FCDLParser(tokens).systemDecl()
    return BuildIRVisitor().visit(tree)

def compile_fcdl(src: pathlib.Path, out_dir: pathlib.Path):
    ir       = parse_file(src)
    decision = plan(ir)

    template_dir = pathlib.Path(pkg.files(generator) / decision["template"])
    #shutil.copytree(template_dir, out_dir, dirs_exist_ok=True)

    # render tiny .env / config.json for demo purposes
    ctx = decision["context"]
    render(template_dir=template_dir, out_dir=out_dir, ctx=ctx)

    (out_dir / "fcdl_context.json").write_text(
        json.dumps(decision["context"],indent=2,
                    default=lambda o: dataclasses.asdict(o)
                        if dataclasses.is_dataclass(o) else str(o))
    )

    print(f"✔  Generated stack in {out_dir}")

def main():
    ap = argparse.ArgumentParser(prog="fcdl")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c   = sub.add_parser("compile")
    c.add_argument("file", type=pathlib.Path)
    c.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    if args.cmd == "compile":
        compile_fcdl(args.file, args.out)

if __name__ == "__main__":
    main()

