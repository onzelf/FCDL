import shutil
import pathlib
import jinja2
import json
import dataclasses

print("Generator")

def render(template_dir: pathlib.Path, out_dir: pathlib.Path, ctx: dict):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
    out_dir.mkdir(parents=True, exist_ok=True)
    for path in template_dir.rglob("*"):
        rel = path.relative_to(template_dir)
        dst = out_dir / rel
        if path.is_dir():
            dst.mkdir(exist_ok=True)
        else:
            if path.suffix == ".j2":
                dst = dst.with_suffix("")  # Remove .j2
                dst.write_text(env.get_template(str(rel)).render(**ctx))
            else:
                shutil.copy2(path, dst)

def generate_stack(ir, decision, out_dir):
    print("Generate the final runnable stack based on planner decision.")
    
    if decision["runtime"] == "flower" and decision["deployment_tool"] == "compose":
        render(
            template_dir=pathlib.Path(__file__).parent / "flower_compose",
            out_dir=out_dir,
            ctx={
                "rounds": ir.rounds or 5,
                "port": ir.port or 5000,
            }
        )
    else:
        raise NotImplementedError(f"No generator available for runtime={decision['runtime']} deployment={decision['deployment_tool']}")
