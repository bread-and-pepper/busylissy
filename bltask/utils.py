def neighborhood(iterable):
    """ 
    When iterating through an item, this function also supllies the previous
    and next item. 
    
    """
    iterator = iter(iterable)
    prev = None
    item = iterator.next()  # throws StopIteration if empty.
    for next in iterator:
        yield (prev,item,next)
        prev = item
        item = next
    yield (prev,item,None)

def structure(nodes):
    """ 
    Defines the structure of the nodes by looking at the previous, current and
    next items in it. Returns the node with a few structural attributes.

        new_level
            ``True`` if the current node is a new level, else ``False``.
    
        parent
            ``True`` if the node is a parent node.
        
        closed_levels
            A list of levels which end AFTER the current item.
    
    """
    for prev, item, next in neighborhood(nodes):
        node = item[0]
        next_node = next[0] if next else None
        prev_node = prev[0] if prev else None

        node.new_level = node.depth > prev_node.depth if prev else True
        node.parent = node.depth == 1 
        if next:
            node.closed_levels = [level for level in range(next_node.depth, node.depth)]
        else:
            node.closed_levels = [level for level in range(0, node.depth)]
    return nodes
