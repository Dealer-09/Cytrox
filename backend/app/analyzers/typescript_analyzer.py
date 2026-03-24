"""TypeScript/JavaScript static analyzer"""
import re
from typing import List, Dict, Any

class TypeScriptAnalyzer:
    """Analyzes TypeScript/JavaScript code for security issues"""
    
    DANGEROUS_FUNCTIONS = {
        'eval': 'eval() allows arbitrary code execution',
        'Function': 'Dynamic function constructor is dangerous',
        'setTimeout': 'setTimeout with string code is dangerous',
        'setInterval': 'setInterval with string code is dangerous',
        'innerHTML': 'innerHTML can lead to XSS vulnerabilities',
        'dangerouslySetInnerHTML': 'React dangerouslySetInnerHTML can lead to XSS',
    }
    
    def __init__(self):
        self.findings = []
    
    async def analyze(self, files: List[str]) -> List[Dict[str, Any]]:
        """Analyze TypeScript/JavaScript files"""
        self.findings = []
        
        for file_path in files:
            if not (file_path.endswith('.ts') or file_path.endswith('.tsx') or 
                   file_path.endswith('.js') or file_path.endswith('.jsx')):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception:
                continue
            
            self._analyze_content(file_path, content)
        
        return self.findings
    
    def _analyze_content(self, file_path: str, content: str):
        """Analyze TypeScript/JavaScript content"""
        lines = content.split('\n')
        
        for pattern, message in self.DANGEROUS_FUNCTIONS.items():
            for i, line in enumerate(lines):
                if re.search(r'\b' + pattern + r'\b', line) and not line.strip().startswith('//'):
                    self.findings.append({
                        'type': 'DANGEROUS_CALL',
                        'severity': 'HIGH',
                        'file_path': file_path,
                        'line_number': i + 1,
                        'message': message,
                        'code_snippet': line.strip()[:100],
                        'recommendation': f'Avoid using {pattern} - use safer alternatives',
                        'confidence': 0.85
                    })
        
        # Check for potential XSS
        xss_patterns = [
            (r'\$\{.+\}', 'Template literal with potentially unsafe content'),
            (r'innerHTML\s*=', 'Direct innerHTML assignment can cause XSS'),
        ]
        
        for pattern, msg in xss_patterns:
            for i, line in enumerate(lines):
                if re.search(pattern, line) and not line.strip().startswith('//'):
                    self.findings.append({
                        'type': 'XSS_VULNERABILITY',
                        'severity': 'MEDIUM',
                        'file_path': file_path,
                        'line_number': i + 1,
                        'message': msg,
                        'code_snippet': line.strip()[:100],
                        'recommendation': 'Use textContent instead of innerHTML or sanitize input',
                        'confidence': 0.7
                    })
