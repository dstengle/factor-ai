#!/usr/bin/env python3
"""
12-Factor App Validator
Automated compliance checking for the twelve-factor methodology
"""

import os
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import ast
import yaml

class TwelveFactorValidator:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.violations = []
        self.warnings = []
        self.passes = []
        
    def validate_all(self) -> Dict:
        """Run all validation checks"""
        print("🔍 Starting 12-Factor Validation...\n")
        
        self.check_factor_1_codebase()
        self.check_factor_2_dependencies()
        self.check_factor_3_config()
        self.check_factor_4_backing_services()
        self.check_factor_5_build_release_run()
        self.check_factor_6_processes()
        self.check_factor_7_port_binding()
        self.check_factor_8_concurrency()
        self.check_factor_9_disposability()
        self.check_factor_10_dev_prod_parity()
        self.check_factor_11_logs()
        self.check_factor_12_admin_processes()
        
        return {
            "violations": self.violations,
            "warnings": self.warnings,
            "passes": self.passes,
            "score": len(self.passes) / (len(self.passes) + len(self.violations)) * 100
        }
    
    def check_factor_1_codebase(self):
        """Factor I: One codebase tracked in revision control"""
        print("📁 Factor I: Codebase")
        
        # Check for Git repository
        git_dir = self.project_path / ".git"
        if git_dir.exists():
            self.passes.append("✓ Git repository found")
        else:
            self.violations.append("✗ No Git repository found")
        
        # Check for multiple apps in one repo (heuristic)
        app_indicators = ["package.json", "requirements.txt", "Gemfile", "pom.xml", "build.gradle"]
        app_roots = []
        for indicator in app_indicators:
            app_roots.extend(self.project_path.rglob(indicator))
        
        if len(set(p.parent for p in app_roots)) > 1:
            self.warnings.append("⚠️  Multiple app roots detected - possible violation")
        
        # Check for .gitignore
        if (self.project_path / ".gitignore").exists():
            self.passes.append("✓ .gitignore present")
        else:
            self.warnings.append("⚠️  No .gitignore file")
        
        print()
    
    def check_factor_2_dependencies(self):
        """Factor II: Explicitly declare and isolate dependencies"""
        print("📦 Factor II: Dependencies")
        
        # Check for dependency manifests
        manifests = {
            "package.json": self._check_npm_deps,
            "requirements.txt": self._check_python_deps,
            "Pipfile": self._check_pipenv_deps,
            "Gemfile": self._check_ruby_deps,
            "pom.xml": self._check_maven_deps,
            "build.gradle": self._check_gradle_deps,
            "go.mod": self._check_go_deps
        }
        
        manifest_found = False
        for manifest, checker in manifests.items():
            if (self.project_path / manifest).exists():
                manifest_found = True
                checker()
        
        if not manifest_found:
            self.violations.append("✗ No dependency manifest found")
        
        # Check for lock files
        lock_files = ["package-lock.json", "yarn.lock", "Pipfile.lock", "Gemfile.lock", "go.sum"]
        lock_found = any((self.project_path / lock).exists() for lock in lock_files)
        
        if lock_found:
            self.passes.append("✓ Dependency lock file present")
        else:
            self.warnings.append("⚠️  No lock file found - exact versions not guaranteed")
        
        print()
    
    def check_factor_3_config(self):
        """Factor III: Store config in the environment"""
        print("🔧 Factor III: Config")
        
        # Check for .env.example or similar
        env_examples = [".env.example", ".env.sample", "env.example"]
        if any((self.project_path / ex).exists() for ex in env_examples):
            self.passes.append("✓ Environment variable documentation found")
        else:
            self.warnings.append("⚠️  No .env.example file documenting required variables")
        
        # Scan for hardcoded secrets/configs
        suspicious_patterns = [
            (r'(password|secret|key|token)\s*=\s*["\'][\w\d]{8,}["\']', "Hardcoded secrets"),
            (r'(localhost|127\.0\.0\.1):\d+', "Hardcoded localhost URLs"),
            (r'https?://[a-zA-Z0-9\.\-]+\.(com|org|net)', "Hardcoded external URLs"),
            (r'[A-Z_]+\s*=\s*["\'][^"\']+["\']', "Possible hardcoded config")
        ]
        
        code_files = list(self.project_path.rglob("*.py")) + \
                    list(self.project_path.rglob("*.js")) + \
                    list(self.project_path.rglob("*.java")) + \
                    list(self.project_path.rglob("*.rb"))
        
        for file in code_files[:20]:  # Sample first 20 files
            try:
                content = file.read_text()
                for pattern, desc in suspicious_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.warnings.append(f"⚠️  {desc} found in {file.relative_to(self.project_path)}")
                        break
            except:
                pass
        
        # Check for environment-specific config files
        bad_configs = ["config/production.json", "config/development.json", 
                      "settings/prod.py", "settings/dev.py"]
        for config in bad_configs:
            if (self.project_path / config).exists():
                self.violations.append(f"✗ Environment-specific config file: {config}")
        
        print()
    
    def check_factor_4_backing_services(self):
        """Factor IV: Treat backing services as attached resources"""
        print("🔌 Factor IV: Backing Services")
        
        # Check if services are referenced via environment variables
        env_patterns = [
            "DATABASE_URL", "REDIS_URL", "RABBITMQ_URL", 
            "ELASTICSEARCH_URL", "MONGODB_URI", "CACHE_URL"
        ]
        
        found_service_configs = False
        for file in self.project_path.rglob("*.py"):
            try:
                content = file.read_text()
                for pattern in env_patterns:
                    if f"os.environ" in content and pattern in content:
                        found_service_configs = True
                        break
            except:
                pass
        
        if found_service_configs:
            self.passes.append("✓ Services referenced via environment variables")
        else:
            self.warnings.append("⚠️  No backing service environment variables detected")
        
        print()
    
    def check_factor_5_build_release_run(self):
        """Factor V: Strictly separate build and run stages"""
        print("🏗️  Factor V: Build, Release, Run")
        
        # Check for Dockerfile
        if (self.project_path / "Dockerfile").exists():
            self.passes.append("✓ Dockerfile present for containerized builds")
            
            # Analyze Dockerfile for good practices
            dockerfile_content = (self.project_path / "Dockerfile").read_text()
            if "COPY" in dockerfile_content and "RUN" in dockerfile_content:
                self.passes.append("✓ Build steps separated in Dockerfile")
        else:
            self.warnings.append("⚠️  No Dockerfile found")
        
        # Check for CI/CD configuration
        ci_files = [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile", ".circleci/config.yml"]
        if any((self.project_path / ci).exists() for ci in ci_files):
            self.passes.append("✓ CI/CD configuration found")
        
        print()
    
    def check_factor_6_processes(self):
        """Factor VI: Execute the app as one or more stateless processes"""
        print("🔄 Factor VI: Processes")
        
        # Check for session storage anti-patterns
        session_violations = [
            (r'session\[.+\]\s*=', "Session storage detected"),
            (r'express-session.*store:\s*new\s*\w+Store', "Server-side session store"),
            (r'sticky.?session', "Sticky sessions detected")
        ]
        
        for file in self.project_path.rglob("*.js"):
            try:
                content = file.read_text()
                for pattern, desc in session_violations:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.violations.append(f"✗ {desc} in {file.relative_to(self.project_path)}")
            except:
                pass
        
        # Check for file system usage beyond temp
        fs_patterns = [
            (r'fs\.write.*(?!\/tmp|\/temp)', "Writing to non-temp filesystem"),
            (r'File\.open.*["\']w["\']', "File write operations detected")
        ]
        
        for pattern, desc in fs_patterns:
            for file in list(self.project_path.rglob("*.js"))[:10]:
                try:
                    if re.search(pattern, file.read_text()):
                        self.warnings.append(f"⚠️  {desc} in {file.name}")
                except:
                    pass
        
        print()
    
    def check_factor_7_port_binding(self):
        """Factor VII: Export services via port binding"""
        print("🚪 Factor VII: Port Binding")
        
        # Check for self-contained web server
        server_patterns = [
            (r'app\.listen\(.*process\.env\.PORT', "Express.js with PORT env var"),
            (r'http\.createServer.*\.listen\(.*process\.env\.PORT', "Node.js HTTP server"),
            (r'port\s*=\s*os\.environ\.get\(["\']PORT', "Python PORT configuration"),
            (r'Rails\.application\.config\.port', "Rails port configuration")
        ]
        
        port_binding_found = False
        for pattern, desc in server_patterns:
            for file in self.project_path.rglob("*"):
                if file.is_file() and file.suffix in [".js", ".py", ".rb"]:
                    try:
                        if re.search(pattern, file.read_text()):
                            self.passes.append(f"✓ {desc} found")
                            port_binding_found = True
                            break
                    except:
                        pass
        
        if not port_binding_found:
            self.warnings.append("⚠️  No PORT environment variable usage detected")
        
        # Check for WAR files or server modules
        if list(self.project_path.rglob("*.war")):
            self.violations.append("✗ WAR files suggest server container dependency")
        
        print()
    
    def check_factor_8_concurrency(self):
        """Factor VIII: Scale out via the process model"""
        print("⚡ Factor VIII: Concurrency")
        
        # Check for process formation files
        if (self.project_path / "Procfile").exists():
            self.passes.append("✓ Procfile defines process types")
            procfile = (self.project_path / "Procfile").read_text()
            if "web:" in procfile and "worker:" in procfile:
                self.passes.append("✓ Multiple process types defined")
        else:
            self.warnings.append("⚠️  No Procfile found")
        
        # Check docker-compose for multi-process setup
        compose_file = self.project_path / "docker-compose.yml"
        if compose_file.exists():
            try:
                compose_data = yaml.safe_load(compose_file.read_text())
                if "services" in compose_data and len(compose_data["services"]) > 1:
                    self.passes.append("✓ Multiple services in docker-compose")
            except:
                pass
        
        print()
    
    def check_factor_9_disposability(self):
        """Factor IX: Maximize robustness with fast startup and graceful shutdown"""
        print("♻️  Factor IX: Disposability")
        
        # Check for graceful shutdown handlers
        shutdown_patterns = [
            (r'process\.on\(["\']SIGTERM', "SIGTERM handler (Node.js)"),
            (r'signal\.signal\(signal\.SIGTERM', "SIGTERM handler (Python)"),
            (r'trap.*TERM', "SIGTERM trap (Shell)")
        ]
        
        graceful_shutdown = False
        for pattern, desc in shutdown_patterns:
            for file in self.project_path.rglob("*"):
                if file.is_file():
                    try:
                        if re.search(pattern, file.read_text()):
                            self.passes.append(f"✓ {desc} found")
                            graceful_shutdown = True
                            break
                    except:
                        pass
        
        if not graceful_shutdown:
            self.warnings.append("⚠️  No graceful shutdown handlers detected")
        
        print()
    
    def check_factor_10_dev_prod_parity(self):
        """Factor X: Keep development, staging, and production as similar as possible"""
        print("🔄 Factor X: Dev/Prod Parity")
        
        # Check Docker usage for consistency
        if (self.project_path / "Dockerfile").exists():
            if (self.project_path / "docker-compose.yml").exists():
                self.passes.append("✓ Docker used for environment consistency")
        
        # Check for environment-specific dependencies
        if (self.project_path / "requirements-dev.txt").exists() or \
           (self.project_path / "package-dev.json").exists():
            self.warnings.append("⚠️  Separate dev dependencies might indicate divergence")
        
        print()
    
    def check_factor_11_logs(self):
        """Factor XI: Treat logs as event streams"""
        print("📋 Factor XI: Logs")
        
        # Check for file-based logging anti-patterns
        log_file_patterns = [
            (r'FileHandler|RotatingFileHandler', "File-based logging (Python)"),
            (r'winston.*filename:', "File-based logging (Node.js)"),
            (r'log4j.*FileAppender', "File-based logging (Java)")
        ]
        
        for pattern, desc in log_file_patterns:
            for file in self.project_path.rglob("*"):
                if file.is_file() and file.suffix in [".py", ".js", ".java"]:
                    try:
                        if re.search(pattern, file.read_text()):
                            self.violations.append(f"✗ {desc} in {file.name}")
                    except:
                        pass
        
        # Check for console/stdout logging
        stdout_patterns = [
            (r'console\.log|console\.error', "Console logging (Node.js)"),
            (r'print\(|logging\.StreamHandler', "stdout logging (Python)"),
            (r'System\.out\.println', "stdout logging (Java)")
        ]
        
        stdout_found = False
        for pattern, desc in stdout_patterns:
            for file in list(self.project_path.rglob("*"))[:20]:
                if file.is_file():
                    try:
                        if re.search(pattern, file.read_text()):
                            stdout_found = True
                            break
                    except:
                        pass
        
        if stdout_found:
            self.passes.append("✓ stdout/console logging detected")
        
        print()
    
    def check_factor_12_admin_processes(self):
        """Factor XII: Run admin/management tasks as one-off processes"""
        print("🛠️  Factor XII: Admin Processes")
        
        # Check for admin scripts
        admin_dirs = ["scripts", "bin", "tasks", "management"]
        admin_found = any((self.project_path / d).exists() for d in admin_dirs)
        
        if admin_found:
            self.passes.append("✓ Admin scripts directory found")
        
        # Check for migration tools
        migration_patterns = ["migrations", "db/migrate", "alembic"]
        if any((self.project_path / m).exists() for m in migration_patterns):
            self.passes.append("✓ Database migration structure found")
        
        print()
    
    # Helper methods for dependency checking
    def _check_npm_deps(self):
        pkg_file = self.project_path / "package.json"
        try:
            pkg_data = json.loads(pkg_file.read_text())
            deps = pkg_data.get("dependencies", {})
            
            # Check for exact versions
            fuzzy_versions = [d for d in deps.values() if any(c in d for c in ["^", "~", "*"])]
            if fuzzy_versions:
                self.warnings.append(f"⚠️  {len(fuzzy_versions)} dependencies with fuzzy versions")
            else:
                self.passes.append("✓ All npm dependencies have exact versions")
        except:
            pass
    
    def _check_python_deps(self):
        req_file = self.project_path / "requirements.txt"
        try:
            content = req_file.read_text()
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
            
            # Check for version pinning
            unpinned = [l for l in lines if "==" not in l and not l.startswith('-')]
            if unpinned:
                self.warnings.append(f"⚠️  {len(unpinned)} Python dependencies without exact versions")
            else:
                self.passes.append("✓ All Python dependencies have exact versions")
        except:
            pass
    
    def _check_pipenv_deps(self):
        self.passes.append("✓ Pipenv used for dependency management")
    
    def _check_ruby_deps(self):
        self.passes.append("✓ Gemfile present for dependency management")
    
    def _check_maven_deps(self):
        self.passes.append("✓ Maven pom.xml present for dependency management")
    
    def _check_gradle_deps(self):
        self.passes.append("✓ Gradle build file present for dependency management")
    
    def _check_go_deps(self):
        self.passes.append("✓ Go modules used for dependency management")


def generate_report(results: Dict):
    """Generate a formatted validation report"""
    print("\n" + "="*60)
    print("📊 12-FACTOR VALIDATION REPORT")
    print("="*60 + "\n")
    
    print(f"Score: {results['score']:.1f}%\n")
    
    if results['passes']:
        print("✅ PASSES:")
        for p in results['passes']:
            print(f"  {p}")
        print()
    
    if results['warnings']:
        print("⚠️  WARNINGS:")
        for w in results['warnings']:
            print(f"  {w}")
        print()
    
    if results['violations']:
        print("❌ VIOLATIONS:")
        for v in results['violations']:
            print(f"  {v}")
        print()
    
    # Recommendations
    print("📝 RECOMMENDATIONS:")
    if results['score'] < 50:
        print("  - Critical: Address violations before deployment")
    elif results['score'] < 80:
        print("  - Moderate: Fix violations and review warnings")
    else:
        print("  - Good: Review warnings for optimization opportunities")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python twelve_factor_validator.py <project_path>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    
    if not os.path.exists(project_path):
        print(f"Error: Path '{project_path}' does not exist")
        sys.exit(1)
    
    validator = TwelveFactorValidator(project_path)
    results = validator.validate_all()
    generate_report(results)
