"""
Pytest configuration and fixtures for LinkBrain tests.
"""

import pytest
from unittest.mock import Mock, MagicMock
from linkbrain import ESP32Controller
from linkbrain.core.command import Command, CommandResponse


@pytest.fixture
def mock_controller():
    """Mock ESP32Controller for testing."""
    controller = Mock(spec=ESP32Controller)
    controller.is_connected.return_value = True
    controller.send_command.return_value = CommandResponse(success=True)
    return controller


@pytest.fixture
def sample_command():
    """Sample command for testing."""
    return Command.gpio_set(12, 1)


@pytest.fixture
def sample_response():
    """Sample successful response."""
    return CommandResponse(success=True, data={"pin": "2", "value": "1"})


@pytest.fixture
def error_response():
    """Sample error response."""
    return CommandResponse(success=False, error="Command failed")