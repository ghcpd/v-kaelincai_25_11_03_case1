# QUICK START GUIDE

## Immediate Execution (Windows PowerShell)

```powershell
cd c:\chatWorkspace
.\run_all.ps1
```

This single command will:
1. Set up Python virtual environments for both projects
2. Install dependencies (pytest)
3. Run all 6 test cases for Project A
4. Run all 6 test cases for Project B
5. Execute performance profiling on synthetic workloads
6. Generate `compare_report.md` with side-by-side metrics

## For Unix/Linux/macOS or Git Bash Users

```bash
cd /c/chatWorkspace  # Or your workspace path
./run_all.sh
```

## Expected Runtime

- Initial setup (first run): 30-60 seconds (includes virtual env creation)
- Subsequent runs: 5-15 seconds (env already exists)

## What to Check After Running

1. **compare_report.md** - Summary table comparing both implementations
2. **project_a/logs/metrics_original.json** - Detailed test results for initial version
3. **project_b/logs/metrics_optimized.json** - Detailed test results for optimized version
4. **project_*/performance/*.txt** - Runtime performance measurements

## Troubleshooting

### "Python not found"
- Ensure Python 3.10+ is installed and on your PATH
- Test with: `python --version`

### "pytest not found" after running setup
- The scripts activate virtual environments automatically
- If running tests manually, activate first:
  ```powershell
  # Windows
  .\.venv\Scripts\Activate.ps1
  
  # Unix/Git Bash
  source .venv/bin/activate
  ```

### Bash scripts won't run on Windows
- **Option 1**: Use PowerShell scripts (`.ps1` files)
- **Option 2**: Install Git Bash or WSL
- **Option 3**: Run individual Python commands:
  ```powershell
  cd project_a
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  pytest
  ```

### Permission denied (Unix/Linux/macOS)
```bash
chmod +x run_all.sh project_a/*.sh project_b/*.sh
./run_all.sh
```

## Manual Test Execution

### Project A Only
```powershell
cd c:\chatWorkspace\project_a
.\run_tests.ps1
```

### Project B Only
```powershell
cd c:\chatWorkspace\project_b
.\run_tests.ps1
```

### Generate Report Without Re-Running Tests
```powershell
cd c:\chatWorkspace
python generate_compare_report.py
```

## Verify Installation

```powershell
# List all Python files
Get-ChildItem -Recurse -Filter "*.py" | Select-Object FullName

# Expected count: 8 Python source/test files + 1 report generator
```

## Next Steps

1. Review `README.md` for comprehensive documentation
2. Review `PROJECT_SUMMARY.md` for technical details
3. Examine `compare_report.md` for performance comparison
4. Inspect source code:
   - `project_a/src/original_code.py` - Table-based implementation
   - `project_b/src/optimized_code.py` - Heap-based implementation
5. Review test cases in `project_*/data/*.json`

## Support

For detailed explanations of:
- Test scenarios → See `PROJECT_SUMMARY.md` section "Test Coverage"
- Algorithms → See `PROJECT_SUMMARY.md` section "Key Differences"
- Metrics → See `PROJECT_SUMMARY.md` section "Evaluation Metrics"
- File structure → See `README.md` section "Project Layout"

---

**Quick validation**: After running `.\run_all.ps1`, you should see:
- ✅ 6/6 tests passing in Project A
- ✅ 6/6 tests passing in Project B
- ✅ Optimized version showing improved performance metrics
- ✅ `compare_report.md` generated with comparison table
