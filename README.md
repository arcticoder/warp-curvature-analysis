# warp-curvature-analysis

## Purpose
Run the warp-bubble time-integration solver on convergence results to extract strong-field curvature diagnostics, then assemble a timeline summary for visualization.

## Workflow Overview
1. **run_strong_curvature.py**  
   - Reads `convergence.ndjson` (and optional AsciiMath `.am`).
   - For each entry, runs the full solver and computes:
     - `max_R` (Ricci scalar)
     - `peak_R2` ($R_{μν}R^{μν}$)
     - Constraint-violation series vs. time.
   - Emits:
     - `strong_curvature.ndjson`
     - `strong_curvature.am`

2. **assemble_visualization.py**  
   - Reads the curvature diagnostics.
   - Detects events (curvature peaks, constraint breaches).
   - Emits:
     - `simulation_summary.ndjson`
     - `simulation_summary.am`

## Inputs
- `convergence.ndjson`  
  JSON lines of:
  ```json
  {
    "parameters": { "grid": 128, "dr": 0.01, "dt": 0.005 },
    "L2_error": 1e-6,
    "Linf_error": 2e-6,
    "order": 2.0
  }
```

-   Optional: `convergence.am` (AsciiMath summary).
    

## Usage Examples

```bash
python run_strong_curvature.py \
  --input convergence.ndjson \
  --input-am convergence.am \
  --output-json strong_curvature.ndjson \
  --output-am   strong_curvature.am

python assemble_visualization.py \
  --input-json strong_curvature.ndjson \
  --input-am   strong_curvature.am \
  --output-json simulation_summary.ndjson \
  --output-am   simulation_summary.am
```

## Outputs

-   **strong\_curvature.ndjson**  
    JSON lines, each:
    
    ```json
    {
      "parameters": { ... },
      "max_R": 0.123,
      "peak_R2": 0.000456,
      "violations": [ [0.0, 1e-7], [0.1, 2e-7], … ]
    }
    ```
    
-   **strong\_curvature.am**  
    AsciiMath summary, e.g.:
    
    ```yaml
    run: grid=128, dr=0.01, dt=0.005, max_R: 0.123, peak_R2: 0.000456
    ```
    
-   **simulation\_summary.ndjson**  
    JSON lines of timeline events:
    
    ```json
    {
      "event": "constraint_violation",
      "time": 0.1,
      "params": { ... }
    }
    ```
    
-   **simulation\_summary.am**  
    AsciiMath timeline notes:
    
    ```csharp
    timeline:
    - at t=0.1: constraint_violation for params { … }
    - at t=0.5: peak_R for params { … }
    ```
    

## Repo Layout

```css
warp-curvature-analysis/
├─ run_strong_curvature.py
├─ assemble_visualization.py
├─ convergence.ndjson
├─ [convergence.am]
├─ strong_curvature.ndjson
├─ strong_curvature.am
├─ simulation_summary.ndjson
├─ simulation_summary.am
└─ README.md
