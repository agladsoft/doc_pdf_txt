from split_scanned_by_paragraph import main

test_number = 'test_61-62'

def test_61_62():
    """
    Test split by border_start_token only (no need for border_end_token)
    """
    left_source = f'tests/{test_number}_left.txt'
    right_source = f'tests/{test_number}_right.txt'
    left_result, right_result = main(left_source, right_source)
    left_result = left_result.strip()
    right_result = right_result.strip()

    with open(f'tests/{test_number}_left_output.txt', 'w') as f:
        f.write(left_result)

    with open(f'tests/{test_number}_right_output.txt', 'w') as f:
        f.write(right_result)

    right_lines = right_result.splitlines()
    assert len(right_lines) == 3
    assert len(right_lines[0]) == 528


if __name__ == '__main__':
    test_61_62()