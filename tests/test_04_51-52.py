from split_scanned_by_paragraph import main

test_number = 'test_04_51-52'

def test_04():
    """
    Test split by border_end_token only (no need for border_start_token)
    """
    left_source = f'tests/{test_number}_left.txt'
    right_source = f'tests/{test_number}_right.txt'
    with open(left_source) as f:
        left_text = f.readlines()
    with open(right_source) as f:
        right_text = f.readlines()

    left_result, right_result = main(left_text, right_text, 200)
    left_result = left_result.strip()
    right_result = right_result.strip()

    with open(f'tests/{test_number}_left_output.txt', 'w') as f:
        f.write(left_result)

    with open(f'tests/{test_number}_right_output.txt', 'w') as f:
        f.write(right_result)

    assert len(right_result.splitlines()) == 7


if __name__ == '__main__':
    test_04()