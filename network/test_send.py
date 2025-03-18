import unittest
from send import send_message_to_c

class TestSendMessageToC(unittest.TestCase):

    def test_send_valid_message(self):
        message = "Hello, C program!"
        result = send_message_to_c(message)
        self.assertTrue(result, "Failed to send a valid message")

    def test_send_empty_message(self):
        message = ""
        result = send_message_to_c(message)
        self.assertFalse(result, "Empty message should not be sent")

    def test_send_special_characters(self):
        message = "Special characters: !@#$%^&*()"
        result = send_message_to_c(message)
        self.assertTrue(result, "Failed to send message with special characters")

    def test_send_long_message(self):
        message = "A" * 1024  # Assuming 1024 is within the acceptable limit
        result = send_message_to_c(message)
        self.assertTrue(result, "Failed to send a long message")

    def test_send_too_long_message(self):
        message = "A" * 65536  # Assuming 65536 exceeds the acceptable limit
        result = send_message_to_c(message)
        self.assertFalse(result, "Message exceeding limit should not be sent")

if __name__ == "__main__":
    unittest.main()
