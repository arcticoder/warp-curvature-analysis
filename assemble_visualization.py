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
        violations = run.get('violations', [])
        if violations:
            # Check if violations contains error strings or numerical data
            if isinstance(violations[0], str):
                # If violations are error messages, create an event for any non-empty violations
                if violations:
                    events.append({
                        'event': 'constraint_violation',
                        'time': None,
                        'params': run.get('parameters', {}),
                        'violation_msg': violations[0]
                    })
            else:
                # If violations are (time, value) tuples
                for t, val in violations:
                    if val > R2_thresh:
                        events.append({
                            'event': 'constraint_violation',
                            'time': t,
                            'params': run.get('parameters', {}),
                            'violation_value': val
                        })
                        break
        
        # peak-R event (use time_of_max_R if available, else None)
        # Only add this event for actual test runs, not header entries
        if run.get('type') in ['test', None] or 'max_R' in run:
            events.append({
                'event': 'peak_R',
                'time': run.get('time_of_max_R'),
                'params': run.get('parameters', {}),
                'max_R': run.get('max_R'),
                'peak_R2': run.get('peak_R2')
            })
    return events

def to_am_timeline(events):
    lines = ["timeline:"]
    for e in events:
        if e['event'] == 'constraint_violation':
            if 'violation_msg' in e:
                lines.append(f"- at t={e['time']}: {e['event']} ({e['violation_msg']}) for params {e['params']}")
            else:
                lines.append(f"- at t={e['time']}: {e['event']} (value={e.get('violation_value')}) for params {e['params']}")
        elif e['event'] == 'peak_R':
            max_R = e.get('max_R', 'N/A')
            peak_R2 = e.get('peak_R2', 'N/A')
            lines.append(f"- at t={e['time']}: {e['event']} (max_R={max_R}, peak_R2={peak_R2}) for params {e['params']}")
        else:
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