"""
Generate trap test cases, run both solvers, and create comparison graphs
"""
import subprocess
import os
import matplotlib.pyplot as plt

# =============================================================================
# CONFIGURATION - UPDATE THESE PATHS!
# =============================================================================
EXACT_SOLVER = "exact_solution/facility_location_exact.py"
APPROX_SOLVER = "blake_approx_solution/facility_location_approx_blake.py"

# If your files are elsewhere, update these paths:
# EXACT_SOLVER = "facility_location_exact.py"
# APPROX_SOLVER = "facility_location_approx_blake.py"

# =============================================================================
# Helper Functions
# =============================================================================

def create_test_case(filename, content):
    """Write test case to file"""
    with open(filename, "w") as f:
        f.write(content)
    return filename


def run_solver(solver_path, test_file):
    """Run solver and extract number of facilities"""
    try:
        if not os.path.exists(solver_path):
            print(f"    ✗ Solver not found: {solver_path}")
            return None
            
        result = subprocess.run(
            ["python", solver_path, test_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout
        
        # Print full output for debugging
        # print(f"    Output:\n{output}\n")
        
        # Method 1: Look for "Facilities opened: X"
        for line in output.split('\n'):
            if "Facilities opened:" in line:
                parts = line.split(':')[1].strip().split()
                if parts and parts[0].isdigit():
                    return int(parts[0])
        
        # Method 2: Look for "Facilities chosen (X):"
        for line in output.split('\n'):
            if "Facilities chosen" in line and '(' in line:
                start = line.index('(') + 1
                end = line.index(')')
                num_str = line[start:end].strip()
                if num_str.isdigit():
                    return int(num_str)
        
        # Method 3: Count facility lines
        in_section = False
        count = 0
        for line in output.split('\n'):
            stripped = line.strip()
            if "Facilities chosen" in stripped or "Open facilities:" in stripped:
                in_section = True
                continue
            if in_section:
                if stripped.startswith('F') and ('at' in stripped or '(' in stripped):
                    count += 1
                elif "Unique Client Assignment" in stripped or "Coverage:" in stripped:
                    break
        
        if count > 0:
            return count
        
        # Method 4: Look for line with just facility names (approx format)
        lines = output.split('\n')
        for i, line in enumerate(lines):
            if "Open facilities:" in line and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                facilities = next_line.split()
                if facilities and all(f.startswith('F') for f in facilities):
                    return len(facilities)
        
        return None
        
    except subprocess.TimeoutExpired:
        print(f"    ✗ Timeout (>60s)")
        return None
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return None


# =============================================================================
# Generate Test Cases
# =============================================================================

print("="*70)
print("GENERATING GREEDY TRAP TEST CASES")
print("="*70)
print()

test_cases = []

# TEST 1: Simple 3-group trap
test_1 = """9 4
C1 10.00 50.00
C2 12.00 50.00
C3 14.00 50.00
C4 40.00 50.00
C5 42.00 50.00
C6 44.00 50.00
C7 70.00 50.00
C8 72.00 50.00
C9 74.00 50.00
F1 12.00 50.00 1
F2 42.00 50.00 1
F3 72.00 50.00 1
F4 27.00 50.00 1
10.0"""
test_cases.append(("Trap 1: 3 Groups", "trap_01.txt", test_1))

# TEST 2: 4-group trap
test_2 = """12 5
C1 10.00 50.00
C2 12.00 50.00
C3 14.00 50.00
C4 50.00 50.00
C5 52.00 50.00
C6 54.00 50.00
C7 90.00 50.00
C8 92.00 50.00
C9 94.00 50.00
C10 130.00 50.00
C11 132.00 50.00
C12 134.00 50.00
F1 12.00 50.00 1
F2 52.00 50.00 1
F3 92.00 50.00 1
F4 132.00 50.00 1
F5 31.00 50.00 1
F6 71.00 50.00 1
F7 111.00 50.00 1
12.0"""
test_cases.append(("Trap 2: 4 Groups", "trap_02.txt", test_2))

# TEST 3: Tight coverage trap
test_3 = """6 4
C1 10.00 50.00
C2 11.00 50.00
C3 30.00 50.00
C4 31.00 50.00
C5 50.00 50.00
C6 51.00 50.00
F1 10.50 50.00 1
F2 30.50 50.00 1
F3 50.50 50.00 1
F4 20.50 50.00 1
11.0"""
test_cases.append(("Trap 3: Tight Coverage", "trap_03.txt", test_3))

# TEST 4: 5-group with multiple baits
test_4 = """15 8
C1 5.00 50.00
C2 10.00 50.00
C3 15.00 50.00
C4 25.00 50.00
C5 30.00 50.00
C6 35.00 50.00
C7 45.00 50.00
C8 50.00 50.00
C9 55.00 50.00
C10 65.00 50.00
C11 70.00 50.00
C12 75.00 50.00
C13 85.00 50.00
C14 90.00 50.00
C15 95.00 50.00
F1 7.50 50.00 1
F2 30.00 50.00 1
F3 50.00 50.00 1
F4 70.00 50.00 1
F5 90.00 50.00 1
F6 20.00 50.00 1
F7 40.00 50.00 1
F8 80.00 50.00 1
9.0"""
test_cases.append(("Trap 4: 5 Groups", "trap_04.txt", test_4))

# TEST 5: Sparse clients
test_5 = """8 5
C1 0.00 50.00
C2 5.00 50.00
C3 30.00 50.00
C4 35.00 50.00
C5 60.00 50.00
C6 65.00 50.00
C7 90.00 50.00
C8 95.00 50.00
F1 2.50 50.00 1
F2 32.50 50.00 1
F3 62.50 50.00 1
F4 92.50 50.00 1
F5 17.50 50.00 1
F6 47.50 50.00 1
F7 77.50 50.00 1
9.0"""
test_cases.append(("Trap 5: Sparse", "trap_05.txt", test_5))

# TEST 6: Dense cluster
test_6 = """10 6
C1 20.00 50.00
C2 22.00 50.00
C3 24.00 50.00
C4 26.00 50.00
C5 28.00 50.00
C6 30.00 50.00
C7 32.00 50.00
C8 80.00 50.00
C9 82.00 50.00
C10 84.00 50.00
F1 25.00 50.00 1
F2 82.00 50.00 1
F3 21.00 50.00 1
F4 29.00 50.00 1
F5 50.00 50.00 1
F6 60.00 50.00 1
8.0"""
test_cases.append(("Trap 6: Dense Cluster", "trap_06.txt", test_6))

# =============================================================================
# Run Both Solvers on Each Test Case
# =============================================================================

print("Running solvers on all test cases...")
print()

results = []

for name, filename, content in test_cases:
    print(f"Testing: {name}")
    create_test_case(filename, content)
    
    # Run exact solver
    print(f"  Running exact solver...", end=" ")
    exact_facs = run_solver(EXACT_SOLVER, filename)
    if exact_facs:
        print(f"✓ {exact_facs} facilities")
    else:
        print("✗ failed")
    
    # Run approx solver
    print(f"  Running approx solver...", end=" ")
    approx_facs = run_solver(APPROX_SOLVER, filename)
    if approx_facs:
        print(f"✓ {approx_facs} facilities")
    else:
        print("✗ failed")
    
    if exact_facs and approx_facs:
        diff = approx_facs - exact_facs
        ratio = approx_facs / exact_facs
        
        if diff > 0:
            print(f"  🎯 TRAP WORKED! Approx uses {diff} extra facilities ({ratio:.2f}x)")
        elif diff == 0:
            print(f"  ✓ Both found same solution ({exact_facs} facilities)")
        else:
            print(f"  ⚠️  Approx better than exact? (shouldn't happen!)")
        
        results.append({
            'name': name,
            'exact': exact_facs,
            'approx': approx_facs,
            'diff': diff,
            'ratio': ratio
        })
    
    print()

# =============================================================================
# Generate Graphs
# =============================================================================

if not results:
    print("No results to plot! Check your solver paths:")
    print(f"  Exact: {EXACT_SOLVER}")
    print(f"  Approx: {APPROX_SOLVER}")
    exit()

print("="*70)
print("GENERATING COMPARISON GRAPHS")
print("="*70)
print()

names = [r['name'] for r in results]
exact_vals = [r['exact'] for r in results]
approx_vals = [r['approx'] for r in results]
diffs = [r['diff'] for r in results]
ratios = [r['ratio'] for r in results]

# Graph 1: Line comparison
plt.figure(figsize=(12, 6))
x = range(len(names))
plt.plot(x, exact_vals, '-o', label='Exact (Optimal)', 
         color='green', linewidth=2.5, markersize=10)
plt.plot(x, approx_vals, '-s', label='Approximation', 
         color='orange', linewidth=2.5, markersize=10)
plt.xlabel('Test Case', fontsize=13, fontweight='bold')
plt.ylabel('Number of Facilities', fontsize=13, fontweight='bold')
plt.title('Exact vs Approximation: Greedy Trap Cases', 
          fontsize=15, fontweight='bold')
plt.xticks(x, [n.replace("Trap ", "").replace(": ", "\n") for n in names], 
           fontsize=10)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('comparison_line.png', dpi=300, bbox_inches='tight')
print("✓ Saved: comparison_line.png")

# Graph 2: Side-by-side bars
plt.figure(figsize=(12, 6))
x_pos = range(len(names))
width = 0.35
plt.bar([i - width/2 for i in x_pos], exact_vals, width, 
        label='Exact', color='green', alpha=0.8)
plt.bar([i + width/2 for i in x_pos], approx_vals, width, 
        label='Approximation', color='orange', alpha=0.8)
plt.xlabel('Test Case', fontsize=13, fontweight='bold')
plt.ylabel('Number of Facilities', fontsize=13, fontweight='bold')
plt.title('Facilities Opened: Exact vs Approximation', 
          fontsize=15, fontweight='bold')
plt.xticks(x_pos, [n.replace("Trap ", "").replace(": ", "\n") for n in names], 
           fontsize=10)
plt.legend(fontsize=12)
plt.grid(True, axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('comparison_bars.png', dpi=300, bbox_inches='tight')
print("✓ Saved: comparison_bars.png")

# Graph 3: Approximation ratio
plt.figure(figsize=(12, 6))
colors = ['red' if r > 1.0 else 'green' for r in ratios]
bars = plt.bar(range(len(names)), ratios, color=colors, alpha=0.7, edgecolor='black')
plt.axhline(y=1.0, color='black', linestyle='--', linewidth=2, 
            label='Optimal (ratio = 1.0)')
plt.xlabel('Test Case', fontsize=13, fontweight='bold')
plt.ylabel('Approximation Ratio (Approx / Exact)', fontsize=13, fontweight='bold')
plt.title('Approximation Quality: How Much Worse?', 
          fontsize=15, fontweight='bold')
plt.xticks(range(len(names)), [n.replace("Trap ", "").replace(": ", "\n") for n in names], 
           fontsize=10)
plt.legend(fontsize=12)
plt.grid(True, axis='y', alpha=0.3)

# Add value labels on bars
for i, (bar, ratio) in enumerate(zip(bars, ratios)):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
             f'{ratio:.2f}x', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('approximation_ratio.png', dpi=300, bbox_inches='tight')
print("✓ Saved: approximation_ratio.png")

# Graph 4: Extra facilities
plt.figure(figsize=(12, 6))
colors = ['red' if d > 0 else 'green' for d in diffs]
bars = plt.bar(range(len(names)), diffs, color=colors, alpha=0.7, edgecolor='black')
plt.axhline(y=0, color='black', linestyle='--', linewidth=2)
plt.xlabel('Test Case', fontsize=13, fontweight='bold')
plt.ylabel('Extra Facilities (Approx - Exact)', fontsize=13, fontweight='bold')
plt.title('How Many Extra Facilities Does Approximation Use?', 
          fontsize=15, fontweight='bold')
plt.xticks(range(len(names)), [n.replace("Trap ", "").replace(": ", "\n") for n in names], 
           fontsize=10)
plt.grid(True, axis='y', alpha=0.3)

# Add value labels on bars
for bar, diff in zip(bars, diffs):
    height = bar.get_height()
    label_y = height + 0.1 if height >= 0 else height - 0.1
    plt.text(bar.get_x() + bar.get_width()/2., label_y,
             f'+{diff}' if diff > 0 else f'{diff}', 
             ha='center', va='bottom' if height >= 0 else 'top', 
             fontweight='bold', fontsize=11)

plt.tight_layout()
plt.savefig('extra_facilities.png', dpi=300, bbox_inches='tight')
print("✓ Saved: extra_facilities.png")

# =============================================================================
# Print Summary
# =============================================================================

print()
print("="*70)
print("SUMMARY")
print("="*70)
print()
print(f"Total test cases: {len(results)}")
print(f"Cases where approx = optimal: {sum(1 for r in ratios if r == 1.0)}")
print(f"Cases where approx > optimal: {sum(1 for r in ratios if r > 1.0)}")

if any(r > 1.0 for r in ratios):
    worst_idx = ratios.index(max(ratios))
    print(f"Worst case: {names[worst_idx]}")
    print(f"  Exact: {exact_vals[worst_idx]}, Approx: {approx_vals[worst_idx]}")
    print(f"  Ratio: {ratios[worst_idx]:.2f}x")

print()
print("Detailed Results:")
print("-" * 70)
print(f"{'Test Case':<25} {'Exact':<8} {'Approx':<8} {'Diff':<8} {'Ratio':<8}")
print("-" * 70)
for r in results:
    symbol = "🎯" if r['diff'] > 0 else "✓"
    print(f"{symbol} {r['name']:<23} {r['exact']:<8} {r['approx']:<8} "
          f"{'+' + str(r['diff']) if r['diff'] > 0 else str(r['diff']):<8} "
          f"{r['ratio']:.2f}x")
print("-" * 70)
print()
print("Graphs saved!")
print("  - comparison_line.png")
print("  - comparison_bars.png")
print("  - approximation_ratio.png")
print("  - extra_facilities.png")