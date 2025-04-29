# compiler/planner.py
"""
Very small “decision engine”:
• looks at orchestration attrs and module types
• returns a dict {template, context} that the generator understands
"""

from typing import Dict
from .ir import SystemIR

def plan(ir: SystemIR) -> Dict:
    orch_attrs = ir.orchestration.attrs
    modules    = {m.mod_type for m in ir.modules.values()}

    # --- choose FL backend -------------------------------------------------
    strategy   = orch_attrs.get("strategy", "FedAvg")
    runtime    = orch_attrs.get("runtime")          # optional hint

    if runtime:
        fl_backend = runtime                         # honour explicit hint
    elif strategy != "FedAvg":
        fl_backend = "flower"
    else:
        fl_backend = "manual"                        # Flask + custom FedAvg

    # --- choose ledger -----------------------------------------------------
    dlt_mods = [m for m in ir.modules.values() if m.mod_type == "DistributedLedger"]
    ledger = dlt_mods[0].attrs["tool"] if dlt_mods else None   # semantic layer already checked 'tool'

    # --- choose infra ------------------------------------------------------
    infra = orch_attrs.get("deployment.tool", "compose")

    template = {
        ("manual",  "compose") : "manual_flask_compose",
        ("flower",  "compose") : "flower_compose",
        ("flower",  "k8s")     : "flower_k8s",
        ("manual",  "k8s")     : "manual_flask_k8s",
    }[(fl_backend, infra)]

    return {
        "template" : template,
        "context"  : {
            "strategy"   : strategy,
            "rounds"     : int(orch_attrs.get("rounds", 10)),
            "fl_backend" : fl_backend,
            "ledger"     : ledger,
            "modules"    : ir.modules,
            "orch_attrs" : orch_attrs,
        }
    }

