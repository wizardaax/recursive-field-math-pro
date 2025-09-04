import subprocess
import os
from recursive_field_math import (
    F, L, r_theta, ratio, ratio_error_bounds, lucas_ratio_cfrac,
    GF_F, GF_L, egypt_4_7_11, signature_summary
)

def _git_status():
    """Get git status information"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            return {"status": "success", "files": result.stdout.strip().split('\n') if result.stdout.strip() else []}
        else:
            return {"status": "error", "message": result.stderr.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _git_add(files="*"):
    """Add files to git staging area"""
    try:
        if files == "*" or files == ".":
            cmd = ['git', 'add', '.']
        else:
            # Handle single file or list of files
            if isinstance(files, str):
                files = [files]
            cmd = ['git', 'add'] + files
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            return {"status": "success", "message": "Files added to staging area"}
        else:
            return {"status": "error", "message": result.stderr.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _git_commit(message="Agent automated commit"):
    """Commit staged changes with a message"""
    try:
        result = subprocess.run(['git', 'commit', '-m', message], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            return {"status": "success", "message": result.stdout.strip()}
        else:
            return {"status": "error", "message": result.stderr.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _git_commit_all(message="Agent automated commit"):
    """Add all files and commit with a message"""
    try:
        # First add all files
        add_result = _git_add(".")
        if add_result["status"] != "success":
            return add_result
        
        # Then commit
        return _git_commit(message)
    except Exception as e:
        return {"status": "error", "message": str(e)}

ROUTES = {
    "fibonacci": lambda a,b: {n:F(n) for n in range(a,b+1)},
    "lucas":     lambda a,b: {n:L(n) for n in range(a,b+1)},
    "field":     lambda a,b: {n:r_theta(n) for n in range(a,b+1)},
    "ratio":     lambda n: {"ratio": ratio(n), "bounds": ratio_error_bounds(n)},
    "cfrac":     lambda n: {"ratio": lucas_ratio_cfrac(n)},
    "gf":        lambda x: {"F": GF_F(x), "L": GF_L(x)},
    "egypt":     lambda : {"num_den": egypt_4_7_11()},
    "sig":       lambda : signature_summary(),
    # Git operations for agent commit functionality
    "git_status": lambda: _git_status(),
    "git_add":   lambda files="*": _git_add(files),
    "git_commit": lambda message="Agent automated commit": _git_commit(message),
    "commit":    lambda message="Agent automated commit": _git_commit_all(message),
}

def query(intent: str, *args):
    intent = (intent or "").strip().lower()
    if intent not in ROUTES:
        return {"error": f"unknown intent: {intent}", "known": sorted(ROUTES.keys())}
    return ROUTES[intent](*args)
