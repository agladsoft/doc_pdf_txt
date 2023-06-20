from split_scanned_by_paragraph import main

def test_03():
    left_source = 'tests/test_03_47_left.txt'
    right_source = 'tests/test_03_47_right.txt'
    with open(left_source) as f:
        left_text = f.readlines()
    with open(right_source) as f:
        right_text = f.readlines()

    left_result, right_result = main(left_text, right_text, 200)
    left_result = left_result.strip()
    right_result = right_result.strip()

    with open(f'tests/test_03_47_left_output.txt', 'w') as f:
        f.write(left_result)

    with open(f'tests/test_03_47_right_output.txt', 'w') as f:
        f.write(right_result)

    assert len(right_result.splitlines()) == 17


if __name__ == '__main__':
    test_03()