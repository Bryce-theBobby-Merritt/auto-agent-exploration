import subprocess
import unittest

class TestCommandSandbox(unittest.TestCase):
    def test_sandbox_execution(self):
        result = subprocess.run(['python', 'command_sandbox/demo/util.py'], capture_output=True, text=True)
        self.assertEqual(result.stdout.strip(), 'hello from sandbox')

if __name__ == '__main__':
    unittest.main()