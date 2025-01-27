from post_process import process


def test_post_process(snapshot):
    output = process([]).decode()

    assert output == snapshot
