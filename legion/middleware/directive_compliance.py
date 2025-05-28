"""Directive compliance checker middleware."""

import logging
from typing import Dict, Tuple, Any, Optional

logger = logging.getLogger(__name__)


class DirectiveCompliance:
    """Checks directive compliance against defined rules."""
    
    def __init__(self):
        self.max_length = 1500
        self.prohibited_keywords = ['sudo', 'rm -rf', 'delete']
        self.required_fields = ['task_id']
    
    def check(self, text: str, metadata: Dict[str, Any], agent_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Check directive compliance.
        
        Returns:
            Tuple of (status, details) where status is 'compliant' or 'non_compliant'
        """
        details = {'checks_failed': []}
        
        # Check length
        if len(text) > self.max_length:
            details['breach_type'] = 'max_length_exceeded'
            return 'non_compliant', details
        
        # Check prohibited keywords
        for keyword in self.prohibited_keywords:
            if keyword in text.lower():
                details['breach_type'] = 'prohibited_keyword'
                return 'non_compliant', details
        
        # Check required metadata fields
        for field in self.required_fields:
            if field not in metadata:
                details['breach_type'] = 'missing_metadata'
                return 'non_compliant', details
        
        return 'compliant', details 