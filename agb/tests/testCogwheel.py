import logging
import unittest
from unittest.mock import patch,MagicMock
from agb.cogwheel import CogwheelLoggerHelper
from discord.embeds import *
import agb.cogwheel
import os

class CogwheelTests(unittest.TestCase):
    def setUp(self):
        self.args = MagicMock()
        self.args.debug = False
    def test_embed(self):
        # Test case 1: Check if the returned object is an instance of discord.Embed
        agb.cogwheel.args = self.args
        result = agb.cogwheel.embed()
        self.assertIsInstance(result, Embed)

        # Test case 2: Check if the footer text is set correctly
        result = agb.cogwheel.embed()
        self.args.debug = True
        self.assertEqual(result.footer.text,"AlphaGameBot version {0}{1}".format(agb.cogwheel.getVersion(), " (development build)" if agb.cogwheel.isDebug(self.args) else ""))

        # Test case 3: Check if the footer icon URL is set correctly
        result = agb.cogwheel.embed()
        self.assertEqual(result.footer.icon_url, "https://static.alphagame.dev/alphagamebot/img/icon.png")

        # Test case 4: Check if the kwargs are passed correctly
        result = agb.cogwheel.embed(title="Test Embed", description="This is a test embed")
        self.assertEqual(result.title, "Test Embed")
        assert result.description == "This is a test embed"

    def test_debugModeEnabled(self):
        with patch.dict(os.environ, {"DEBUG": "1"}):
            self.assertEqual(agb.cogwheel.isDebug(), True)
        argp = MagicMock()
        argp.debug = True
        self.assertEqual(agb.cogwheel.isDebug(argp), True)

    def test_debugModeDisabled(self):
        # Test case 1: Check if the debug mode is set correctly
        with patch.dict(os.environ, {"DEBUG": ""}):
            self.assertEqual(agb.cogwheel.isDebug(), False)
        with patch.dict(os.environ, {"DEBUG": "no"}):
            self.assertEqual(agb.cogwheel.isDebug(), False)
        with patch.dict(os.environ, {"DEBUG": "0"}):
            self.assertEqual(agb.cogwheel.isDebug(), False)
        with patch.dict(os.environ, {"DEBUG": "false"}):
            self.assertEqual(agb.cogwheel.isDebug(), False)

        argp = MagicMock()
        argp.debug = False
        self.assertEqual(agb.cogwheel.isDebug(argp), False)
if __name__ == "__main__":
    unittest.main()
