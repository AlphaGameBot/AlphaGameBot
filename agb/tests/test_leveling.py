import unittest
from unittest.mock import patch, mock_open
import json
from importlib import reload

# Import the module to be tested
import agb.system.leveling as leveling

class TestLeveling(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data='{"levels": [{"level": 1, "messages_required": 10}, {"level": 2, "messages_required": 20}]}')
    def test_levels_loading(self, mock_file):
        # Reload the module to trigger the file read
        with patch('agb.system.leveling.json.load', return_value={"levels": [{"level": 1, "messages_required": 10}, {"level": 2, "messages_required": 20}]}):
            reload(leveling)
        
        # Check if levels are loaded correctly
        expected_levels = [{"level": 1, "messages_required": 10}, {"level": 2, "messages_required": 20}]
        self.assertEqual(leveling.levels, expected_levels)
    
    def test_get_level_from_message_count(self):
        # Test case 1: Check if the level is calculated correctly
        leveling.levels = [{"level": 1, "messages_required": 10}, {"level": 2, "messages_required": 20}]
        result = leveling.get_level_from_message_count(15)
        self.assertEqual(result, 1)

        # Test case 2: Check if the level is calculated correctly
        leveling.levels = [{"level": 1, "messages_required": 10}, {"level": 2, "messages_required": 20}]
        result = leveling.get_level_from_message_count(25)
        self.assertEqual(result, 2)

if __name__ == "__main__":
    unittest.main()