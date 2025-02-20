import unittest
from unittest.mock import MagicMock
from piqueserver.core_commands.moderation import get_ban_arguments, has_digits
from piqueserver.core_commands.movement import do_move


class TestCoreCommands(unittest.TestCase):
    def test_has_digits(self):
        test_cases = [("1day", True), ("day", False), ("  1", True)]
        for case in test_cases:
            input, expect = case
            self.assertEqual(has_digits(input), expect)

    def test_get_ban_arguments(self):
        connection = MagicMock()
        connection.protocol.default_ban_time = 9001
        self.assertEqual(connection.protocol.default_ban_time, 9001)
        test_cases = [
            {
                "name": "Simple",
                "expect": (20 * 60, "too twenty"),
                "args": ["20", "too twenty"]
            },
            {
                "name": "Only reason",
                "expect": (9001, "blah blah blah blah"),
                "args": ["blah", "blah", "blah", "blah"]
            },
            {
                "name": "Perma",
                "expect": (None, "tabs"),
                "args": ["perma", "tabs"]
            },
            {
                "name": "No args",
                "expect": (9001, None),
                "args": []
            },
            {
                "name": "Simple duration",
                "expect": (60 * 60, "ab"),
                "args": ["1hour", "ab"]
            },
            {
                "name": "Invalid duration",
                "expect": (),
                "args": ["1dia", "?"],
                "ex": ValueError
            },
        ]
        for case in test_cases:
            print(case["name"])
            if "ex" in case:
                with self.assertRaises(case["ex"]):
                    get_ban_arguments(connection, case["args"])
                continue
            got = get_ban_arguments(connection, case["args"])
            self.assertTupleEqual(got, case["expect"])


    def setUp(self):
        """
        Setup a mock connection object before testing.
        """
        self.mock_connection = MagicMock()
        self.mock_connection.name = "Mock_Player"
        self.mock_connection.admin = False
        self.mock_connection.rights.move_others = False
        self.mock_connection.invisible = False
        self.mock_connection.protocol.players = {"Mock_Player": self.mock_connection}
        self.mock_connection.protocol.map.get_height.return_value = 50

    def test_move_self_sector(self):
        """
        Test moving self to a sector.
        """

        do_move(self.mock_connection, ["A1"], branch_coverage=branch_coverage)

        self.assertTrue(branch_coverage["init_index_0"])
        self.assertTrue(branch_coverage["target_sector"])
        self.assertTrue(branch_coverage["move_self"])
        self.assertFalse(branch_coverage["move_other"])
        self.assertTrue(branch_coverage["set_location_self"])
        self.assertFalse(branch_coverage["set_location_other"])
        self.assertTrue(branch_coverage["broadcast_message"])
        self.assertFalse(branch_coverage["silent_message"])
        self.assertTrue(branch_coverage["evaluate_silent_false"])
        self.assertFalse(branch_coverage["evaluate_silent_true"])
        self.assertFalse(branch_coverage["error_requires_player"])
        self.assertFalse(branch_coverage["error_invalid_params"])
        self.assertFalse(branch_coverage["error_invalid_arg_count"])


    def test_move_self_coordinates(self):
        """
        Test moving self to specific coordinates.
        """

        do_move(self.mock_connection, ["50", "50", "10"], branch_coverage=branch_coverage)

        self.assertTrue(branch_coverage["init_index_0"])
        self.assertTrue(branch_coverage["target_coordinates"])
        self.assertTrue(branch_coverage["move_self"])
        self.assertFalse(branch_coverage["move_other"])
        self.assertTrue(branch_coverage["set_location_self"])
        self.assertFalse(branch_coverage["set_location_other"])
        self.assertTrue(branch_coverage["broadcast_message"])
        self.assertFalse(branch_coverage["silent_message"])
        self.assertTrue(branch_coverage["evaluate_silent_false"])
        self.assertFalse(branch_coverage["evaluate_silent_true"])
        self.assertFalse(branch_coverage["error_requires_player"])
        self.assertFalse(branch_coverage["error_invalid_params"])
        self.assertFalse(branch_coverage["error_invalid_arg_count"])

    @classmethod
    def tearDownClass(cls):
        """
        After all tests, print final branch coverage results to show the total branch coverage from all of the tests.
        """
        print_branch_coverage(branch_coverage)


branch_coverage = {
        "init_index_1": False,
        "init_index_0": False,
        "target_sector": False,
        "target_coordinates": False,
        "error_invalid_params": False,
        "move_self": False,
        "error_requires_player": False,
        "player_exists": False,
        "move_other": False,
        "error_permission_denied": False,
        "permission_granted": False,
        "error_invalid_arg_count": False,
        "evaluate_silent_true": False,
        "evaluate_silent_false": False,
        "set_location_self": False,
        "set_location_other": False,
        "silent_message": False,
        "broadcast_message": False,
}

def print_branch_coverage(branch_coverage):
    """
    Prints the total branch coverage and which branches that were visited during the tests.
    :param: branch_coverage (dict): dictionary holding all of the branches (keys represents their unique "id")
    """
    print("\n---Branch Coverage Results---")
    for branch, marked in branch_coverage.items():
        print(f"{branch}: {'Executed' if marked else 'Not executed'}")
    print("\nTotal coverage: ", (sum(branch_coverage.values()) / len(branch_coverage)) * 100 , "%\n")
    print("---End---\n")

if __name__ == "__main__":
    unittest.main()

    
