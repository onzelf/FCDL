import antlr4
from .fcdl.FCDLParser import FCDLParser
from .fcdl.FCDLVisitor import FCDLVisitor
from .ir import *

class BuildIRVisitor(FCDLVisitor):
    # system "X" { ... }
    def visitSystemDecl(self, ctx:FCDLParser.SystemDeclContext):
        name = ctx.STRING().getText().strip('"')
        version = ctx.VERSION().getText() if ctx.VERSION() else "1.0"
        ir = SystemIR(name=name, version=version)

        body_ctx = ctx.systemBody()
        for child in body_ctx.children:
            res = self.visit(child)
            if isinstance(res, Module):
                ir.modules[res.name] = res
            elif isinstance(res, Orchestration):
                ir.orchestration = res

        # --- semantic checks ---
        if ir.orchestration is None:
            raise RuntimeError("FC spec: exactly ONE orchestration block required")

        dlts = [m for m in ir.modules.values() if m.mod_type == "DistributedLedger"]
        if dlts:
            if len(dlts) > 1:
                raise RuntimeError("Only one DistributedLedger module allowed")
            if "tool" not in dlts[0].attrs:
                raise RuntimeError("DLT found but missing 'tool' attribute")

        return ir

    # module "Foo" (...)
    def visitModuleDecl(self, ctx:FCDLParser.ModuleDeclContext):
        name = ctx.STRING().getText().strip('"')
        mod_type = ctx.ID().getText() 
        attrs = self._attrs(ctx.attrList())
        layers = [self.visit(l) for l in ctx.layerDecl()] if ctx.layerDecl() else []
        return Module(name, mod_type, attrs, layers)

    # layer (...)
    def visitLayerDecl(self, ctx:FCDLParser.LayerDeclContext):
        attrs = self._attrs(ctx.attrList())
        return NeuralLayer(attrs.pop("type", "Unknown"), attrs)

    # orchestration (...)
    def visitOrchestrationDecl(self, ctx:FCDLParser.OrchestrationDeclContext):
        return Orchestration(self._attrs(ctx.attrList()))

    # util
    '''
    def _attrs(self, ctx):
        if ctx is None: return {}
        text = ctx.getText()[1:-1]           # strip parentheses
        pairs = [p.strip() for p in text.split(',') if p.strip()]
        return {k.strip(): v.strip().strip('"') for k,v in (p.split('=') for p in pairs)}
    '''
     # ------------------------------------------------------------------
    def _attrs(self, ctx):
        """
        ctx can be:
        • None
        • a single FCDLParser.AttrListContext
        • a list of such contexts   (when rule has attrList*)
        Returns a dict of key→value strings.
        """
        if ctx is None:
            return {}

        # normalise to list
        nodes = ctx if isinstance(ctx, list) else [ctx]

        result = {}
        for node in nodes:
            text = node.getText()[1:-1]              # strip surrounding (...)
            if not text:
                continue
            for pair in text.split(','):
                k, v = pair.split('=', 1)
                result[k.strip()] = v.strip().strip('"')

        return result
    # ------------------------------------------------------------------


