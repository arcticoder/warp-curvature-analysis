# Technical Documentation: warp-curvature-analysis

## Overview

The `warp-curvature-analysis` repository provides specialized tools for analyzing strong-field curvature effects in warp-bubble spacetime simulations. It processes convergence study results to extract detailed curvature diagnostics, constraint violations, and timeline summaries for visualization and analysis.

## Mathematical Foundation

### Curvature Invariants

The analysis computes key curvature invariants that characterize the gravitational field strength:

#### Ricci Scalar (R)
```
R = gᵘᵛRᵤᵥ
```
- Measures the local curvature of spacetime
- Critical for identifying strong-field regions

#### Ricci Tensor Contraction (R²)
```
R² = RᵤᵥRᵘᵛ
```
- Provides a coordinate-invariant measure of field strength
- Essential for detecting potential curvature singularities

### Constraint Violation Analysis

General relativity imposes constraint equations that must be satisfied:

#### Hamiltonian Constraint
```
H = R⁽³⁾ - KᵢⱼKᵢⱼ + K² - 16πρ = 0
```

#### Momentum Constraints
```
Mᵢ = Dⱼ(Kᵢⱼ - γᵢⱼK) - 8πSᵢ = 0
```

Violations of these constraints indicate numerical errors or physical inconsistencies.

## Algorithm Description

### Two-Stage Processing Pipeline

#### Stage 1: Curvature Extraction (`run_strong_curvature.py`)

1. **Input Processing**: Read convergence study results from `convergence.ndjson`
2. **Solver Integration**: Run full warp-bubble solver for each parameter set
3. **Diagnostic Computation**: Extract curvature invariants and constraint violations
4. **Output Generation**: Emit structured curvature data

#### Stage 2: Timeline Assembly (`assemble_visualization.py`)

1. **Event Detection**: Identify significant curvature events and constraint violations
2. **Timeline Construction**: Organize events chronologically
3. **Summary Generation**: Create visualization-ready timeline data

### Data Flow Architecture

```
convergence.ndjson → run_strong_curvature.py → strong_curvature.ndjson
                                           ↓
                  assemble_visualization.py → simulation_summary.ndjson
```

## Dependencies and Integration

### Core Dependencies

1. **solver.py** (from related repositories)
   - Provides RK4 time integration
   - Computes curvature tensors and invariants
   - Must accept JSON parameters via stdin

2. **convergence.ndjson** (from warp-convergence-analysis)
   - Contains validated parameter sets from convergence studies
   - Ensures analysis uses numerically verified configurations

### Integration Points

- **warp-convergence-analysis**: Provides input convergence data
- **warp-solver-validation**: Supplies solver implementation
- **warp-bubble-einstein-equations**: Defines Einstein field equations
- **warp-bubble-connection-curvature**: Provides curvature computation methods

## Implementation Details

### Solver Interface

The curvature analysis expects a specific solver interface:

```python
# Input: JSON parameters via stdin
{
  "parameters": {"grid": 128, "dr": 0.01, "dt": 0.005},
  "L2_error": 1e-6,
  "Linf_error": 2e-6,
  "order": 2.0
}

# Output: JSON diagnostics via stdout
{
  "max_R": 0.123,
  "peak_R2": 0.000456,
  "violations": [[0.0, 1e-7], [0.1, 2e-7], ...]
}
```

### Error Handling

```python
def run_solver(params):
    try:
        p = subprocess.run(['python', 'solver.py'], ...)
        return json.loads(p.stdout.strip())
    except subprocess.CalledProcessError as e:
        # Handle solver execution errors
    except json.JSONDecodeError as e:
        # Handle malformed output
```

### Event Detection Algorithm

```python
def detect_events(curvature_data):
    events = []
    
    # Detect curvature peaks
    if curvature_data['max_R'] > threshold:
        events.append({
            'event': 'curvature_peak',
            'time': find_peak_time(curvature_data),
            'magnitude': curvature_data['max_R']
        })
    
    # Detect constraint violations
    for time, violation in curvature_data['violations']:
        if violation > violation_threshold:
            events.append({
                'event': 'constraint_violation',
                'time': time,
                'magnitude': violation
            })
    
    return events
```

## Output Formats

### NDJSON Structure

#### strong_curvature.ndjson
```json
{
  "parameters": {"grid": 128, "dr": 0.01, "dt": 0.005},
  "max_R": 0.123,
  "peak_R2": 0.000456,
  "violations": [[0.0, 1e-7], [0.1, 2e-7]]
}
```

#### simulation_summary.ndjson
```json
{
  "event": "constraint_violation",
  "time": 0.1,
  "params": {"grid": 128, "dr": 0.01},
  "magnitude": 2e-7
}
```

### AsciiMath Summaries

#### strong_curvature.am
```
run: grid=128, dr=0.01, dt=0.005, max_R: 0.123, peak_R2: 0.000456
```

#### simulation_summary.am
```
timeline:
- at t=0.1: constraint_violation for params {grid: 128, dr: 0.01}
- at t=0.5: curvature_peak for params {grid: 128, dr: 0.01}
```

## Configuration and Usage

### Basic Usage

```bash
# Extract curvature diagnostics
python run_strong_curvature.py \
  --input convergence.ndjson \
  --output-json strong_curvature.ndjson \
  --output-am strong_curvature.am

# Assemble timeline visualization
python assemble_visualization.py \
  --input-json strong_curvature.ndjson \
  --input-am strong_curvature.am \
  --output-json simulation_summary.ndjson \
  --output-am simulation_summary.am
```

### Parameter Interpretation

- **max_R**: Peak Ricci scalar value (indicates maximum spacetime curvature)
- **peak_R2**: Peak Ricci tensor contraction (coordinate-invariant field strength)
- **violations**: Time series of constraint violation magnitudes

## Analysis Interpretation

### Physical Significance

#### Curvature Thresholds
- **Low curvature**: R < 0.1 (weak-field regime)
- **Moderate curvature**: 0.1 < R < 1.0 (intermediate regime)
- **Strong curvature**: R > 1.0 (strong-field regime, potential instabilities)

#### Constraint Violations
- **Numerical errors**: Violations growing linearly with time
- **Physical inconsistencies**: Violations growing exponentially
- **Acceptable levels**: Violations < 1e-6 for most applications

### Diagnostic Applications

1. **Stability Analysis**: Monitor constraint violation growth
2. **Field Strength Assessment**: Evaluate curvature invariant magnitudes
3. **Event Detection**: Identify critical points in spacetime evolution
4. **Validation**: Verify solver accuracy through constraint preservation

## Related Work

### Theoretical Background

- ADM formalism and 3+1 decomposition
- Curvature invariants in general relativity
- Constraint violation analysis in numerical relativity

### Computational Methods

- Runge-Kutta time integration
- Finite difference spatial discretization
- Constraint-preserving evolution schemes

### Related Repositories

- **warp-convergence-analysis**: Provides validated input parameters
- **warp-solver-validation**: Supplies solver implementations
- **warp-bubble-einstein-equations**: Mathematical foundation
- **warp-bubble-connection-curvature**: Curvature computation methods

## Future Enhancements

### Advanced Analysis Features

1. **Spectral Analysis**: Fourier decomposition of curvature evolution
2. **Stability Metrics**: Lyapunov exponent computation
3. **Phase Space Analysis**: Attractor identification in parameter space
4. **Uncertainty Quantification**: Error propagation analysis

### Visualization Extensions

1. **Interactive Dashboards**: Real-time curvature monitoring
2. **3D Visualization**: Spatial curvature distribution plots
3. **Animation Generation**: Time-evolution movies
4. **Comparative Analysis**: Multi-run comparison tools

### Performance Optimization

1. **Parallel Processing**: Multi-core curvature computation
2. **Memory Optimization**: Streaming data processing for large datasets
3. **GPU Acceleration**: CUDA-based curvature calculations
4. **Adaptive Sampling**: Intelligent event detection and refinement

## References

### Numerical Relativity

- Alcubierre, M. "Introduction to 3+1 Numerical Relativity"
- Baumgarte, T.W. & Shapiro, S.L. "Numerical Relativity: Solving Einstein's Equations on the Computer"

### Curvature Analysis

- Wald, R.M. "General Relativity"
- Poisson, E. "A Relativist's Toolkit: The Mathematics of Black-Hole Mechanics"

### Computational Methods

- Press, W.H. et al. "Numerical Recipes in C: The Art of Scientific Computing"
- LeVeque, R.J. "Finite Difference Methods for Ordinary and Partial Differential Equations"
