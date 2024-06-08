package taskB;

/**
 * This class is used as a node for the linked list That is, we start linking
 * blocks together
 */
public class BlockNode {

    // current block and a link to the next block
    private Block block;
    private BlockNode next;

    /**
     * Default constructor
     */
    public BlockNode() {
	next = null;
	block = null;
    }

    /**
     * Constructor of BlockNode
     * 
     * @param d Block of memory at this node
     * @param n next node linked to current node
     */
    public BlockNode(Block d, BlockNode n) {
	this.block = d;
	this.next = n;
    }

    /**
     * Setter for the next BlockNode link
     * 
     * @param n next BlockNode to be linked to
     */
    public void setNext(BlockNode n) {
	next = n;
    }

    /**
     * Sets the block of memory for current node.
     * 
     * @param d Block to be set.
     */
    public void setBlock(Block d) {
	block = d;
    }

    /**
     * Gets the next BlockNode that's linked.
     * 
     * @return next BlockNode linked to current.
     */
    public BlockNode getNext() {
	return next;
    }

    /**
     * Getter for the block stored at this BlockNode if one.
     * 
     * @return block to get
     */
    public Block getBlock() {
	return block;
    }

}
