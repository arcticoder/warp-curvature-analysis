import argparse
import json
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser(
        description="Assemble timeline of curvature events from diagnostics."
    )
    p.add_argument('--input-json', required=True, help='strong_curvature.ndjson')
    p.add_argument('--input-am',   required=True, help='strong_curvature.am')
    p.add_argument('--output-json', required=True, help='simulation_summary.ndjson')
    p.add_argument('--output-am',   required=True, help='simulation_summary.am')
    return p.parse_args()

def load_json(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

def load_am(path):
    return Path(path).read_text()

def detect_events(diagnostics, R2_thresh=1e-6):
    events = []
    for run in diagnostics:
        # constraint-violation event
        for t, val in run.get('violations', []):
            if val > R2_thresh:
                events.append({
                    'event': 'constraint_violation',
                    'time': t,
                    'params': run.get('parameters', {})
                })
                break
        # peak-R event (use time_of_max_R if available, else None)
        events.append({
            'event': 'peak_R',
            'time': run.get('time_of_max_R'),
            'params': run.get('parameters', {})
        })
    return events

def to_am_timeline(events):
    lines = ["timeline:"]
    for e in events:
        lines.append(f"- at t={e['time']}: {e['event']} for params {e['params']}")
    return "\n".join(lines)

def main():
    args = parse_args()
    diag = load_json(args.input_json)
    _ = load_am(args.input_am)  # metadata or thresholds could be parsed here
    events = detect_events(diag)
    # write summary JSON
    with open(args.output_json, 'w') as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")
    # write AsciiMath notes
    am_out = to_am_timeline(events)
    with open(args.output_am, 'w') as f:
        f.write(am_out)

if __name__ == '__main__':
    main()