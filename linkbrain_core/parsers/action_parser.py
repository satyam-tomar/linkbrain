"""
Parser for converting LLM output to device actions.
"""

import json
import re
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DeviceAction:
    """Represents a single device action."""
    device: str
    action: str
    
    def __repr__(self) -> str:
        return f"DeviceAction(device='{self.device}', action='{self.action}')"

@dataclass
class ParsedResponse:
    """Parsed response from LLM."""
    actions: List[DeviceAction]
    message: str
    raw_output: str
    
    def __repr__(self) -> str:
        return f"ParsedResponse(actions={len(self.actions)}, message='{self.message}')"


class ActionParser:
    """
    Parses LLM output into executable device actions.
    """
    
    VALID_ACTIONS = {"on", "off", "status"}
    
    def __init__(self):
        """Initialize parser."""
        logger.info("Action parser initialized")
    
    def extract_json(self, text: str) -> str:
        """
        Extract JSON from LLM response (handles markdown code blocks).
        
        Args:
            text: Raw LLM output
        
        Returns:
            Extracted JSON string
        """
        # Remove markdown code blocks if present
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return text.strip()
    
    def validate_action(self, action: str) -> bool:
        """
        Validate action string.
        
        Args:
            action: Action to validate
        
        Returns:
            True if valid
        """
        return action.lower() in self.VALID_ACTIONS
    
    def parse(self, llm_output: str) -> ParsedResponse:
        """
        Parse LLM output into structured actions.
        
        Args:
            llm_output: Raw output from LLM
        
        Returns:
            Parsed response with actions and message
        
        Raises:
            ValueError: If parsing fails
        """
        try:
            logger.debug(f"Parsing LLM output: {llm_output[:100]}...")
            
            # Extract JSON
            json_str = self.extract_json(llm_output)
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Validate structure
            if not isinstance(data, dict):
                raise ValueError("Response is not a JSON object")
            
            if "actions" not in data:
                raise ValueError("Missing 'actions' field in response")
            
            # Parse actions
            actions = []
            for action_data in data.get("actions", []):
                if not isinstance(action_data, dict):
                    logger.warning(f"Skipping invalid action: {action_data}")
                    continue
                
                device = action_data.get("device", "").strip()
                action = action_data.get("action", "").strip().lower()
                
                # Validate
                if not device:
                    logger.warning("Skipping action with no device name")
                    continue
                
                if not self.validate_action(action):
                    logger.warning(f"Invalid action '{action}', skipping")
                    continue
                
                actions.append(DeviceAction(device=device, action=action))
            
            message = data.get("message", "Actions parsed successfully")
            
            parsed = ParsedResponse(
                actions=actions,
                message=message,
                raw_output=llm_output
            )
            
            logger.info(f"Parsed {len(actions)} actions from LLM output")
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise ValueError(f"Invalid JSON in LLM response: {e}")
        except Exception as e:
            logger.error(f"Parsing error: {e}")
            raise ValueError(f"Failed to parse LLM output: {e}")