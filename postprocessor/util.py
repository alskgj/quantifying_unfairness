import logging

logger = logging.getLogger(__name__)


def jain(sizes):
    """Calculates jains fairness of a list of har objects"""
    # if sizes is a har object, transform it to an int
    sizes = [element.size if hasattr(element, 'size') else element for element in sizes]
    n = len(sizes)
    return sum(sizes) ** 2 / (n * sum([t ** 2 for t in sizes]))

