import more_itertools as mit


class MyIter(mit.peekable):
    """
    A few hack on iterable to be more user friendly for parsing files

    Changes:
    Strips lines before yielding iterator
    Keeps track of line number in file
    """
    def __init__(self, iterable):
        super().__init__(iterable)
        self._position = 0
        self._current_line = ''

    def __next__(self):
        self._position += 1
        self._current_line = super().__next__().strip()
        return self._current_line

    def jump(self, num):
        """
        Jump forward the specified number of elements in the iterator
        :return: the line n-steps forward
        """
        if num > 0:
            raise IndexError('Cannot jump backwards yet')

        for _ in range(num-1):
            next(self)
        return next(self)

    def peek(self):
        return super().peek().strip()

    def isempty(self):
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
    mi = MyIter(open('myiter.py'))
    peeked = mi.peek()
    for line in mi:
        assert line == mi._current_line
        assert peeked == line

        if not mi.isempty():
            peeked = mi.peek()
