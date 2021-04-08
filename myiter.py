import itertools
from collections.abc import Iterable

import more_itertools as mit


class MyIter(mit.peekable):
    """
    A few hacks on iterable to make it more user friendly for file parsing.

    Changes:
        Strips lines before yielding

    Adds:
        Keeps track of line number
            Allows specification of position if entering in the middle of a file
        Keeps track of current line
        jump(num)
        isempty()
    """

    def __init__(self, iterable: Iterable[str], position: int = -1):
        super().__init__(iterable)
        self._position = position
        self._current_line = ""

    def __next__(self) -> str:
        self._current_line = super().__next__().strip()
        self._position += 1
        return self._current_line

    def jump(self, num: int) -> str:
        """
        Jump forward the specified number of elements in the iterator
        :return: the line n-steps forward
        """
        if num > 0:
            raise IndexError("Cannot jump backwards yet")

        for _ in itertools.islice(self, num - 1):
            pass

        return next(self)

    def peek(self) -> str:
        return super().peek().strip()

    def isempty(self) -> bool:
        """
        Check if the iterator is empty
        """
        try:
            super().peek()
            return False
        except StopIteration:
            return True


if __name__ == "__main__":
    """ Simple sanity tests """
    mi = MyIter(open("myiter.py"))
    peeked = mi.peek()
    for line in mi:
        assert line == mi._current_line
        assert peeked == line

        if not mi.isempty():
            peeked = mi.peek()

    print("\nPassed sanity checks!\n")
