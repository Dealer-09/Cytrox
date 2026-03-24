"""Python static analyzer using AST"""
import ast
import re
from typing import List, Dict, Any
import os

class PythonAnalyzer:
    """Analyzes Python code for security issues"""
    
    DANGEROUS_FUNCTIONS = {
        'eval': {'severity': 'CRITICAL', 'message': 'eval() allows arbitrary code execution'},
        'exec': {'severity': 'CRITICAL', 'message': 'exec() allows arbitrary code execution'},
        '__import__': {'severity': 'HIGH', 'message': 'Dynamic imports are dangerous'},
        'compile': {'severity': 'HIGH', 'message': 'compile() with user input is risky'},
        'open': {'severity': 'MEDIUM', 'message': 'File operations should be restricted'},
        'subprocess.call': {'severity': 'HIGH', 'message': 'subprocess.call() with shell=True is dangerous'},
        'subprocess.Popen': {'severity': 'HIGH', 'message': 'subprocess.Popen() with shell=True is dangerous'},
        'os.system': {'severity': 'HIGH', 'message': 'os.system() is dangerous, use subprocess instead'},
        'pickle.loads': {'severity': 'HIGH', 'message': 'pickle.loads() with untrusted data is dangerous'},
    }
    
    SECRET_PATTERNS = {
        'AWS_KEY': r'AKIA[0-9A-Z]{16}',
        'GITHUB_TOKEN': r'ghp_[0-9a-zA-Z]{36}',
        'PRIVATE_KEY': r'-----BEGIN RSA PRIVATE KEY-----',
        'JWT_TOKEN': r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
    }
    
    def __init__(self):
        self.findings = []
    
    async def analyze(self, files: List[str]) -> List[Dict[str, Any]]:
        """Analyze Python files for vulnerabilities"""
        self.findings = []
        
        for file_path in files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception:
                continue
            
            # Analyze for secrets
            self._analyze_secrets(file_path, content)
            
            # Analyze AST
            try:
                tree = ast.parse(content)
                self._analyze_ast(file_path, tree, content)
            except Exception:
                pass
        
        return self.findings
    
    def _analyze_ast(self, file_path: str, tree: ast.AST, content: str):
        """Analyze Python AST for dangerous patterns"""
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node.func)
                
                if func_name in self.DANGEROUS_FUNCTIONS:
                    danger_info = self.DANGEROUS_FUNCTIONS[func_name]
                    self.findings.append({
                        'type': 'DANGEROUS_CALL',
                        'severity': danger_info['severity'],
                        'file_path': file_path,
                        'line_number': node.lineno,
                        'message': danger_info['message'],
                        'code_snippet': lines[node.lineno - 1] if node.lineno <= len(lines) else '',
                        'recommendation': f'Avoid using {func_name}() - review the code for safer alternatives',
                        'confidence': 0.95
                    })
            
            # Check for use of pickle
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == 'pickle':
                        self.findings.append({
                            'type': 'DANGEROUS_IMPORT',
                            'severity': 'MEDIUM',
                            'file_path': file_path,
                            'line_number': node.lineno,
                            'message': 'pickle module detected - ensure only trusted data is deserialized',
                            'code_snippet': lines[node.lineno - 1] if node.lineno <= len(lines) else '',
                            'recommendation': 'Use safer serialization formats like JSON',
                            'confidence': 0.9
                        })
    
    def _get_function_name(self, node) -> str:
        """Extract function name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return ''
    
    def _analyze_secrets(self, file_path: str, content: str):
        """Detect exposed secrets using patterns"""
        lines = content.split('\n')
        
        for pattern_name, pattern in self.SECRET_PATTERNS.items():
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    # Avoid false positives in comments
                    if line.strip().startswith('#'):
                        import logging
                        logging.debug(f'Skipping comment line with {pattern_name}')
                        continue
                    
                    self.findings.append({
                        'type': 'EXPOSED_SECRET',
                        'severity': 'CRITICAL',
                        'file_path': file_path,
                        'line_number': i + 1,
                        'message': f'Potential {pattern_name} detected',
                        'code_snippet': line.strip()[:100],  # Truncate for safety
                        'recommendation': 'Move secrets to environment variables or a secrets manager',
                        'confidence': 0.8
                    })
