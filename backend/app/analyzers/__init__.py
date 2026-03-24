"""
Multi-language static analyzer orchestrator
Supports: Python, TypeScript, Go, Rust, Java, C++
"""
import asyncio
from typing import Dict, List, Any, Optional
from app.analyzers.python_analyzer import PythonAnalyzer
from app.analyzers.typescript_analyzer import TypeScriptAnalyzer
from app.analyzers.go_analyzer import GoAnalyzer, RustAnalyzer, JavaAnalyzer, CppAnalyzer

class MultiLanguageAnalyzer:
    """Orchestrates analysis across multiple languages"""
    
    def __init__(self):
        self.analyzers = {
            'python': PythonAnalyzer(),
            'typescript': TypeScriptAnalyzer(),
            'go': GoAnalyzer(),
            'rust': RustAnalyzer(),
            'java': JavaAnalyzer(),
            'cpp': CppAnalyzer(),
        }
        self.language_extensions = {
            '.py': 'python',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.js': 'typescript',
            '.jsx': 'typescript',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'cpp',
            '.h': 'cpp',
        }
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect language from file extension"""
        import os
        _, ext = os.path.splitext(file_path)
        return self.language_extensions.get(ext.lower())
    
    async def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Analyze repository across all languages"""
        import os
        
        findings = []
        languages_detected = {}
        total_files = 0
        analyzed_files = 0
        
        # Collect all applicable files
        file_analysis_map = {}
        
        for root, dirs, files in os.walk(repo_path):
            # Skip common unanalyzed directories
            dirs[:] = [d for d in dirs if d not in 
                      {'.git', '__pycache__', 'node_modules', 'dist', 'build', '.venv', 'venv'}]
            
            for file in files:
                file_path = os.path.join(root, file)
                lang = self.detect_language(file_path)
                
                if lang:
                    total_files += 1
                    if lang not in file_analysis_map:
                        file_analysis_map[lang] = []
                    file_analysis_map[lang].append(file_path)
                    languages_detected[lang] = languages_detected.get(lang, 0) + 1
        
        # Run analyzers in parallel
        tasks = []
        for lang, files in file_analysis_map.items():
            if lang in self.analyzers:
                tasks.append(self._analyze_language(lang, files))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    continue
                if isinstance(result, dict):
                    findings.extend(result['findings'])
                    analyzed_files += result.get('files_analyzed', 0)
        
        return {
            'findings': findings,
            'total_files': total_files,
            'analyzed_files': analyzed_files,
            'languages_detected': languages_detected
        }
    
    async def _analyze_language(self, language: str, files: List[str]) -> Dict[str, Any]:
        """Analyze files for a specific language"""
        analyzer = self.analyzers.get(language)
        if not analyzer:
            return {'findings': [], 'files_analyzed': 0}
        
        return {
            'findings': await analyzer.analyze(files),
            'files_analyzed': len(files)
        }
