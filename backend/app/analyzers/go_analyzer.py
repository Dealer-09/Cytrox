"""Go, Rust, Java, C++ analyzers"""
from typing import List, Dict, Any

class GoAnalyzer:
    async def analyze(self, files: List[str]) -> List[Dict[str, Any]]:
        findings = []
        for file_path in files:
            if not file_path.endswith('.go'):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                findings.extend(self._check_dangerous_patterns(file_path, content))
            except:
                pass
        return findings
    
    def _check_dangerous_patterns(self, file_path: str, content: str) -> List[Dict]:
        findings = []
        lines = content.split('\n')
        
        # Check for SQL injection risks
        import re
        if re.search(r'fmt\.Sprintf.*SELECT', content):
            findings.append({
                'type': 'SQL_INJECTION_RISK',
                'severity': 'HIGH',
                'file_path': file_path,
                'message': 'Potential SQL injection - use parameterized queries',
                'recommendation': 'Use prepared statements with placeholders',
                'confidence': 0.8
            })
        
        return findings

class RustAnalyzer:
    async def analyze(self, files: List[str]) -> List[Dict[str, Any]]:
        findings = []
        for file_path in files:
            if not file_path.endswith('.rs'):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                findings.extend(self._check_dangerous_patterns(file_path, content))
            except:
                pass
        return findings
    
    def _check_dangerous_patterns(self, file_path: str, content: str) -> List[Dict]:
        findings = []
        import re
        
        # Check for unsafe blocks
        if 'unsafe {' in content:
            findings.append({
                'type': 'UNSAFE_CODE',
                'severity': 'MEDIUM',
                'file_path': file_path,
                'message': 'Unsafe code block detected - ensure proper safety',
                'recommendation': 'Review unsafe code for potential vulnerabilities',
                'confidence': 0.9
            })
        
        return findings

class JavaAnalyzer:
    async def analyze(self, files: List[str]) -> List[Dict[str, Any]]:
        findings = []
        for file_path in files:
            if not file_path.endswith('.java'):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                findings.extend(self._check_dangerous_patterns(file_path, content))
            except:
                pass
        return findings
    
    def _check_dangerous_patterns(self, file_path: str, content: str) -> List[Dict]:
        findings = []
        import re
        
        # Check for SQL injection risks
        if re.search(r'Statement|executeQuery\("SELECT', content):
            findings.append({
                'type': 'SQL_INJECTION_RISK',
                'severity': 'HIGH',
                'file_path': file_path,
                'message': 'Potential SQL injection - use PreparedStatement',
                'recommendation': 'Use PreparedStatement instead of Statement',
                'confidence': 0.85
            })
        
        return findings

class CppAnalyzer:
    async def analyze(self, files: List[str]) -> List[Dict[str, Any]]:
        findings = []
        for file_path in files:
            if not any(file_path.endswith(ext) for ext in ['.cpp', '.cc', '.cxx', '.h', '.c']):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                findings.extend(self._check_dangerous_patterns(file_path, content))
            except:
                pass
        return findings
    
    def _check_dangerous_patterns(self, file_path: str, content: str) -> List[Dict]:
        findings = []
        import re
        
        # Check for buffer overflow risks
        if re.search(r'strcpy|gets|sprintf\(', content):
            findings.append({
                'type': 'BUFFER_OVERFLOW_RISK',
                'severity': 'CRITICAL',
                'file_path': file_path,
                'message': 'Dangerous function detected - risk of buffer overflow',
                'recommendation': 'Use strndcpy, fgets, or snprintf instead',
                'confidence': 0.95
            })
        
        return findings
