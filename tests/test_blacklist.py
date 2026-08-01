import unittest

from bot.parser import is_blacklisted_input, query_blacklisted_input


class BlacklistTests(unittest.TestCase):
    def test_training_purposes_is_blacklisted(self) -> None:
        text = "I am calling for training purposes"
        self.assertTrue(is_blacklisted_input(text))
        self.assertTrue(query_blacklisted_input(text))


if __name__ == "__main__":
    unittest.main()
