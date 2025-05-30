import argparse
import json
import subprocess
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser(
        description="Run full warp-bubble solver runs and extract curvature diagnostics."
    )
    p.add_argument('--input',       required=True, help='convergence.ndjson')
    p.add_argument('--input-am',    help='convergence.am (AsciiMath)')
    p.add_argument('--output-json', required=True, help='strong_curvature.ndjson')
    p.add_argument('--output-am',   required=True, help='strong_curvature.am')
    return p.parse_args()

def load_convergence_json(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

def load_convergence_am(path):
    return Path(path).read_text() if path and Path(path).exists() else None

def run_solver(params):
    # assume solver.py takes JSON on stdin and emits JSON diagnostics on stdout
    p = subprocess.run(
        ['python', 'solver.py'],
        input=json.dumps(params),
        text=True, capture_output=True, check=True
    )
    return json.loads(p.stdout)

def to_asciimath(entries):
    lines = []
    for e in entries:
        specs = ", ".join(f"{k}={v}" for k, v in e.items() if k not in ('violations',))
        lines.append(f"run: {specs}, max_R: {e['max_R']}, peak_R2: {e['peak_R2']}")
    return "\n".join(lines)

def main():
    args = parse_args()
    conv = load_convergence_json(args.input)
    # ignore AM input for now; metadata could be parsed similarly
    results = []
    for entry in conv:
        diag = run_solver(entry.get('parameters', entry))
        results.append({
            **entry,
            'max_R': diag['max_R'],
            'peak_R2': diag['peak_R2'],
            'violations': diag['violations']
        })
    # write JSON output
    with open(args.output_json, 'w') as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    # write AsciiMath summary
    am_text = to_asciimath(results)
    with open(args.output_am, 'w') as f:
        f.write(am_text)

if __name__ == '__main__':
    main()