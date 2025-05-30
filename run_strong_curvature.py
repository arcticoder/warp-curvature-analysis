import argparse
import json
import subprocess
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser(
        description="Run full warp-bubble solver runs and extract curvature diagnostics."
    )
    p.add_argument('--input',       required=True, help='convergence.ndjson')
    p.add_argument('--output-json', required=True, help='strong_curvature.ndjson')
    p.add_argument('--output-am',   required=True, help='strong_curvature.am')
    return p.parse_args()

def load_convergence_json(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

def run_solver(params):
    # assume solver.py takes JSON on stdin and emits JSON diagnostics on stdout
    try:
        p = subprocess.run(
            ['python', 'solver.py'],
            input=json.dumps(params),
            text=True, capture_output=True, check=True,
            cwd=Path(__file__).parent  # Ensure we're in the right directory
        )
        stdout_clean = p.stdout.strip()
        if not stdout_clean:
            raise ValueError("Empty output from solver")
        return json.loads(stdout_clean)
    except subprocess.CalledProcessError as e:
        print(f"Solver failed with error: {e}")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {repr(p.stdout)}")
        raise
    except json.JSONDecodeError as e:
        print(f"Failed to parse solver output as JSON: {e}")
        print(f"Raw output: {repr(p.stdout)}")
        raise

def to_asciimath(entries):
    lines = []
    for e in entries:
        # Extract key parameters for cleaner display
        name = e.get('name', 'unknown')
        max_R = e.get('max_R', 'N/A')
        peak_R2 = e.get('peak_R2', 'N/A')
        lines.append(f"run: {name}, max_R: {max_R}, peak_R2: {peak_R2}")
    return "\n".join(lines)

def main():
    args = parse_args()
    conv = load_convergence_json(args.input)
    results = []
    for entry in conv:
        # Skip header entries and order entries, only process test entries
        if entry.get('type') in ['header', 'order']:
            continue
        # For test entries, use the entry itself as parameters
        diag = run_solver(entry)
        results.append({
            **entry,
            'max_R': diag['max_R'],
            'peak_R2': diag['peak_R2'],
            'time_of_max_R': diag.get('time_of_max_R', 0.0),  # Use get() with default
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