#!/usr/bin/env python3
"""
Legion Local Environment Doctor

Validates developer's local Legion setup after Docker removal.
Fast execution (≤ 5 sec), clear pass/fail markers, exits non-zero on critical failures.
"""

import argparse
import os
import platform
import socket
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Guard imports with fallbacks
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

# Status indicators
CHECK_PASS = "✅"
CHECK_FAIL = "❌"
CHECK_WARN = "⚠️"

class DoctorCheck:
    def __init__(self, name: str, critical: bool = True):
        self.name = name
        self.critical = critical
        self.status = None
        self.message = ""

class LegionDoctor:
    def __init__(self, allow_dirty: bool = False):
        self.allow_dirty = allow_dirty
        self.checks: List[DoctorCheck] = []
        self.fatal_count = 0
        self.warning_count = 0
        self.workspace_root = Path.cwd()
        
    def add_check(self, name: str, critical: bool = True) -> DoctorCheck:
        check = DoctorCheck(name, critical)
        self.checks.append(check)
        return check
        
    def check_python_version(self) -> DoctorCheck:
        """Check Python version ≥ 3.11"""
        check = self.add_check("Python ≥ 3.11", critical=True)
        
        version = sys.version_info
        if version >= (3, 11):
            check.status = CHECK_PASS
            check.message = f"Python {version.major}.{version.minor}.{version.micro}"
        else:
            check.status = CHECK_FAIL
            check.message = f"Python {version.major}.{version.minor}.{version.micro} (requires ≥ 3.11)"
            
        return check
        
    def check_env_ports_file(self) -> Tuple[DoctorCheck, Dict[str, Any]]:
        """Check .env.ports present & loadable"""
        check = self.add_check(".env.ports present & loadable", critical=True)
        env_vars = {}
        
        env_ports_path = self.workspace_root / ".env.ports"
        if not env_ports_path.exists():
            check.status = CHECK_FAIL
            check.message = ".env.ports file not found"
            return check, env_vars
            
        try:
            with open(env_ports_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
                        
            check.status = CHECK_PASS
            check.message = f"Loaded {len(env_vars)} variables"
        except Exception as e:
            check.status = CHECK_FAIL
            check.message = f"Failed to parse .env.ports: {e}"
            
        return check, env_vars
        
    def check_required_env_vars(self, env_vars: Dict[str, str]) -> DoctorCheck:
        """Check required LEGION_*_PORT environment variables"""
        check = self.add_check("Required env vars set", critical=True)
        
        # Check for Redis port with alternatives
        redis_vars = ["LEGION_REDIS_PORT", "REDIS_PORT"]
        redis_found = any(var in env_vars or var in os.environ for var in redis_vars)
        
        # Check for orchestrator port with alternatives
        orchestrator_vars = ["PORT_ALLOCATOR_ORCHESTRATOR", "BACKEND_PORT", "LEGION_API_PORT"]
        orchestrator_found = any(var in env_vars or var in os.environ for var in orchestrator_vars)
        
        # Check for web UI port with alternatives
        webui_vars = ["PORT_ALLOCATOR_WEB_UI", "FRONTEND_PORT", "WEB_API_PORT"]
        webui_found = any(var in env_vars or var in os.environ for var in webui_vars)
        
        missing = []
        if not redis_found:
            missing.append("Redis port (LEGION_REDIS_PORT/REDIS_PORT)")
        if not orchestrator_found:
            missing.append("Orchestrator port (PORT_ALLOCATOR_ORCHESTRATOR/BACKEND_PORT)")
        if not webui_found:
            missing.append("Web UI port (PORT_ALLOCATOR_WEB_UI/FRONTEND_PORT)")
                
        if missing:
            check.status = CHECK_FAIL
            check.message = f"Missing: {', '.join(missing)}"
        else:
            check.status = CHECK_PASS
            check.message = f"All required port vars present"
            
        return check
        
    def check_port_availability(self, env_vars: Dict[str, str]) -> DoctorCheck:
        """Check port availability for LEGION_*_PORT"""
        check = self.add_check("Port availability", critical=True)
        
        # Collect all LEGION/PORT_ALLOCATOR ports
        port_vars = {}
        all_vars = {**env_vars, **dict(os.environ)}
        
        for key, value in all_vars.items():
            if key.startswith(("LEGION_", "PORT_ALLOCATOR_")) and key.endswith("_PORT"):
                try:
                    port_vars[key] = int(value)
                except ValueError:
                    continue
                    
        if not port_vars:
            check.status = CHECK_WARN
            check.message = "No LEGION_*_PORT variables found"
            return check
            
        conflicts = []
        for var_name, port in port_vars.items():
            if self._is_port_in_use(port):
                if HAS_PSUTIL:
                    process_info = self._get_port_process_info(port)
                    conflicts.append(f"{var_name}:{port} ({process_info})")
                else:
                    conflicts.append(f"{var_name}:{port}")
                    
        if conflicts:
            check.status = CHECK_FAIL
            check.message = f"Ports in use: {', '.join(conflicts)}"
        else:
            check.status = CHECK_PASS
            check.message = f"All {len(port_vars)} ports available"
            
        return check
        
    def check_redis_connectivity(self, env_vars: Dict[str, str]) -> DoctorCheck:
        """Check Redis reachable at LEGION_REDIS_PORT"""
        check = self.add_check("Redis connectivity", critical=True)
        
        if not HAS_REDIS:
            check.status = CHECK_FAIL
            check.message = "redis package not installed"
            return check
            
        # Get Redis port with alternatives
        redis_port = None
        all_vars = {**env_vars, **dict(os.environ)}
        
        for var_name in ["LEGION_REDIS_PORT", "REDIS_PORT"]:
            if var_name in all_vars:
                try:
                    redis_port = int(all_vars[var_name])
                    break
                except ValueError:
                    continue
        
        if redis_port is None:
            redis_port = 7600  # Default from dev_start.sh (760X range)
            
        try:
            r = redis.Redis(host="localhost", port=redis_port, socket_timeout=2)
            response = r.ping()
            if response:
                check.status = CHECK_PASS
                check.message = f"Redis responding on port {redis_port}"
            else:
                check.status = CHECK_FAIL
                check.message = f"Redis not responding on port {redis_port}"
        except Exception as e:
            check.status = CHECK_FAIL
            check.message = f"Redis connection failed on port {redis_port}: {str(e)[:50]}"
            
        return check
        
    def check_required_packages(self) -> DoctorCheck:
        """Check required Python packages installed"""
        check = self.add_check("Required Python packages", critical=True)
        
        required_packages = ["uvicorn", "fastapi", "redis", "psutil"]
        missing = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
                
        if missing:
            check.status = CHECK_FAIL
            check.message = f"Missing packages: {', '.join(missing)}"
        else:
            check.status = CHECK_PASS
            check.message = f"All packages available ({len(required_packages)})"
            
        return check
        
    def check_required_scripts(self) -> DoctorCheck:
        """Check scripts present & executable"""
        check = self.add_check("Required scripts", critical=False)
        
        required_scripts = [
            "scripts/dev_start.sh",
            "scripts/start_all.sh"
        ]
        
        missing = []
        not_executable = []
        
        for script_path in required_scripts:
            full_path = self.workspace_root / script_path
            if not full_path.exists():
                missing.append(script_path)
            elif not os.access(full_path, os.X_OK):
                not_executable.append(script_path)
                
        if missing or not_executable:
            check.status = CHECK_WARN
            issues = []
            if missing:
                issues.append(f"missing: {', '.join(missing)}")
            if not_executable:
                issues.append(f"not executable: {', '.join(not_executable)}")
            check.message = "; ".join(issues)
        else:
            check.status = CHECK_PASS
            check.message = f"All scripts present ({len(required_scripts)})"
            
        return check
        
    def check_git_cleanliness(self) -> DoctorCheck:
        """Check Git cleanliness (optional with --allow-dirty)"""
        check = self.add_check("Git cleanliness", critical=False)
        
        if self.allow_dirty:
            check.status = CHECK_PASS
            check.message = "Skipped (--allow-dirty)"
            return check
            
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=3,
                cwd=self.workspace_root
            )
            
            if result.returncode != 0:
                check.status = CHECK_WARN
                check.message = "Git status check failed"
            elif result.stdout.strip():
                dirty_files = len(result.stdout.strip().split('\n'))
                check.status = CHECK_WARN
                check.message = f"{dirty_files} unstaged changes"
            else:
                check.status = CHECK_PASS
                check.message = "Working directory clean"
                
        except Exception as e:
            check.status = CHECK_WARN
            check.message = f"Git check failed: {str(e)[:30]}"
            
        return check
        
    def _is_port_in_use(self, port: int) -> bool:
        """Check if port is in use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", port))
                return result == 0
        except Exception:
            return False
            
    def _get_port_process_info(self, port: int) -> str:
        """Get process info for port (requires psutil)"""
        if not HAS_PSUTIL:
            return "unknown process"
            
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    if conn.pid:
                        try:
                            process = psutil.Process(conn.pid)
                            return f"PID {conn.pid}: {process.name()}"
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            return f"PID {conn.pid}: unknown"
                    return "unknown process"
        except Exception:
            pass
        return "unknown process"
        
    def run_all_checks(self) -> int:
        """Run all checks and return exit code"""
        print("Legion Environment Doctor")
        print("=" * 30)
        
        # Run checks in order
        self.check_python_version()
        env_check, env_vars = self.check_env_ports_file()
        
        # Only run dependent checks if env file loaded successfully
        if env_check.status == CHECK_PASS:
            self.check_required_env_vars(env_vars)
            self.check_port_availability(env_vars)
            self.check_redis_connectivity(env_vars)
        
        self.check_required_packages()
        self.check_required_scripts()
        self.check_git_cleanliness()
        
        # Print results
        for check in self.checks:
            print(f"[{check.status}] {check.name}: {check.message}")
            
            if check.status == CHECK_FAIL and check.critical:
                self.fatal_count += 1
            elif check.status == CHECK_WARN:
                self.warning_count += 1
                
        # Summary
        print("-" * 30)
        if self.fatal_count == 0 and self.warning_count == 0:
            print("Status: All checks passed ✅")
            return 0
        else:
            status_parts = []
            if self.fatal_count > 0:
                status_parts.append(f"{self.fatal_count} fatal")
            if self.warning_count > 0:
                status_parts.append(f"{self.warning_count} warnings")
            
            print(f"Status: {', '.join(status_parts)}")
            return 1 if self.fatal_count > 0 else 0

def main():
    parser = argparse.ArgumentParser(
        description="Legion Local Environment Health Check"
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Skip Git cleanliness check"
    )
    
    args = parser.parse_args()
    
    doctor = LegionDoctor(allow_dirty=args.allow_dirty)
    exit_code = doctor.run_all_checks()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 