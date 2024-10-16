import unittest
from unittest.mock import patch, mock_open
from importlib import reload
import json

import agb.system.leveling as leveling

class TestLeveling(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open)
    def test_get_level_from_message_count(self, mock_file_open):
        # Define the side effect function for mock_open
        def mock_file_open_side_effect(file, *args, **kwargs):
            if file == 'assets/points.json':
                return mock_open(read_data='{"MESSAGE": 1, "COMMAND": 5}').return_value
            elif file == 'assets/levels.json':
                return mock_open(read_data='{"levels": [{"level": 1, "points_required": 10}, {"level": 2, "points_required": 50}]}').return_value
            else:
                raise FileNotFoundError(f"No such file or directory: '{file}'")

        mock_file_open.side_effect = mock_file_open_side_effect

        # Re-import the module to apply the mock
        reload(leveling)

        messages = 50
        expected_level = 2  # Assuming level 2 requires 50 messages
        result = leveling.get_level_from_message_count(messages)
        self.assertEqual(result, expected_level)

if __name__ == '__main__':
    unittest.main()
