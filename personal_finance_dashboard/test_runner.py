import unittest
import os

# Ensure FLASK_ENV is set to 'testing' before importing app parts for tests
# This is crucial if tests are run directly via this script
# and not through 'flask test' which might set it.
os.environ['FLASK_ENV'] = 'testing'

# Discover and run tests
if __name__ == '__main__':
    # Create a TestLoader instance
    loader = unittest.TestLoader()

    # Discover tests in the 'tests' directory
    # Ensure this path is correct relative to where test_runner.py is
    # Assuming test_runner.py is in personal_finance_dashboard/
    suite = loader.discover(start_dir='./tests')

    # Create a TextTestRunner instance
    runner = unittest.TextTestRunner(verbosity=2) # Added verbosity for more output

    # Run the tests
    result = runner.run(suite)

    # Exit with a status code that reflects the test outcome
    # This is useful for CI/CD pipelines
    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)
