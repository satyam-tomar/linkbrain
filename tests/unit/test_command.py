"""
Unit tests for Command class.
"""

import pytest
from linkbrain.core.command import Command, CommandType, CommandResponse


class TestCommand:
    """Test Command class."""
    
    def test_gpio_set_command(self):
        """Test GPIO set command creation."""
        cmd = Command.gpio_set(2, 1)
        assert cmd.cmd_type == CommandType.GPIO_SET
        assert cmd.params["pin"] == 12
        assert cmd.params["value"] == 1
    
    def test_gpio_get_command(self):
        """Test GPIO get command creation."""
        cmd = Command.gpio_get(13)
        assert cmd.cmd_type == CommandType.GPIO_GET
        assert cmd.params["pin"] == 13
    
    def test_status_command(self):
        """Test status command creation."""
        cmd = Command.status()
        assert cmd.cmd_type == CommandType.STATUS
        assert cmd.params == {}
    
    def test_to_protocol_string(self):
        """Test protocol string conversion."""
        cmd = Command.gpio_set(12, 1)
        protocol_str = cmd.to_protocol_string()
        assert "gpio_set" in protocol_str
        assert "pin=12" in protocol_str
        assert "value=1" in protocol_str
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        cmd = Command.gpio_set(12, 1)
        cmd_dict = cmd.to_dict()
        assert cmd_dict["type"] == "gpio_set"
        assert cmd_dict["params"]["pin"] == 12
        assert cmd_dict["params"]["value"] == 1


class TestCommandResponse:
    """Test CommandResponse class."""
    
    def test_successful_response(self):
        """Test successful response parsing."""
        response = CommandResponse.from_string("OK:pin=12,value=1")
        assert response.success is True
        assert response.data["pin"] == "12"
        assert response.data["value"] == "1"
    
    def test_error_response(self):
        """Test error response parsing."""
        response = CommandResponse.from_string("ERROR:Invalid pin")
        assert response.success is False
        assert response.error == "Invalid pin"
    
    def test_simple_ok_response(self):
        """Test simple OK response."""
        response = CommandResponse.from_string("OK")
        assert response.success is True
        assert response.data == {}
    
    def test_invalid_response_format(self):
        """Test invalid response format."""
        response = CommandResponse.from_string("INVALID")
        assert response.success is False
        assert "Invalid response format" in response.error