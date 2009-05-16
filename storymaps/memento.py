"""Abstract interface classes for the Memento design pattern that is used to
save and restore the state of the application."""

class Originator:
    """Interfance to be implemented by objects whose state can be saved and
    restored."""

    def create_memento(self):
        """Return a memento containing a snapshot of the object's current state.
        """
        raise NotImplementedError

    def restore_memento(self,memento):
        """Restore the object's internal state from a memento."""
        raise NotImplementedError

class Memento:
    """A memento is a passive object that holds the internal state of an
    originator object (not necessarily the entire state of the object, only
    that which needs to be saved and restored). For each class that implements
    the Originator interface there should be a corresponding class that
    implements the Memento interface,"""

    def __init__(self):
        """Different items of state should be passed as arguments to the init
        method, the init method should save these items as atrributes."""
        raise NotImplementedError

    def __str__(self):
        """__str__ should be implemented to implement text export of mementos.
        """
        raise NotImplementedError

class Caretaker:
    """A class that requests a memento from an originator, holds on to the
    memento, and later passes it back to the originator, to carry out a save
    and restore."""

    def save(self):
        """Save the current state of the memento to file."""
        raise NotImplementedError

    def load(self):
        """Restore the current state of the memento from file."""
        raise NotImplementedError

    def export(self):
        """Export the current state of the memento to a text file."""
        raise NotImplementedError