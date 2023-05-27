from split_scanned_by_paragraph import main

def test_02():
    left_source = 'tests/test_02_left.txt'
    right_source = 'tests/test_02_right.txt'
    left_result, right_result = main(left_source, right_source)
    left_result = left_result.strip()
    right_result = right_result.strip()

    with open(f'tests/test_02_left_output.txt', 'w') as f:
        f.write(left_result)

    with open(f'tests/test_02_right_output.txt', 'w') as f:
        f.write(right_result)

    assert len(right_result.splitlines()) == 32


if __name__ == '__main__':
    test_02()