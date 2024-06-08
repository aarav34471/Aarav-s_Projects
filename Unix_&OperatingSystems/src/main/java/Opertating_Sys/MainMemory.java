package taskB;

import java.util.ArrayList;
import java.util.List;

/**
 * This class main purpose is to be a linked list for the current blocks of
 * memory that are placed or free for the simulation of First Fit, Best Fit, and
 * Worst Fit memory allocation methods.
 */
public class MainMemory {
	
	public static final int TOTAL_BYTES = 1024; 

    private BlockNode start;
    private BlockNode end;
    private int size;

    /**
     * Constructor, initialize linked list
     */
    public MainMemory() {
	start = null;
	end = null;
	size = 0;
    }

    /**
     * Checks if linked list is empty
     * 
     * @return True if empty, false if not
     */
    public boolean isEmpty() {
	return start == null;
    }

    /**
     * Gets the size of linked list
     * 
     * @return size of linked list
     */
    public int getSize() {
	return size;
    }

    /**
     * Inserts Block at start of linked list, best to be used to initialize first
     * node.
     * 
     * @param block Block of memory to insert.
     */
    public void insertAtStart(Block block) {
	BlockNode nptr = new BlockNode(block, null);
	size++;
	if (start == null) {
	    start = nptr;
	    end = start;
	} else {
	    nptr.setNext(start);
	    start = nptr;
	}
    }

    /**
     * First fit insert, this method goes through the linked list finding the first
     * place it can insert the block into memory.
     * 
     * @param the Process proc to insert into memory
     * @return True if successfully inserted block of memory, False if failed.
     */
    public boolean firstFitInsert(Process proc) {
	Block block = new Block(proc);
	BlockNode nptr = new BlockNode(block, null);

	if (start == null) {
	    start = nptr;
	    end = start;
	    return true;
	} else {

	    BlockNode curr = start;

	    // look at all available slots/holes in memory
	    // select the first available position of suitable size for block
	    while (curr != null) {

		// enough available space in memory identified
		if (curr.getBlock().canPlace(block.getProcess())) {

		    // get the end memory location for available block curr
		    int end = curr.getBlock().getHole().getEnd();

		    // add the process in memory
		    curr.getBlock().setProcess(block.getProcess());

		    // take only what we need from memory
		    int block_start = curr.getBlock().getHole().getStart();
		    int memory_needs = block.getProcess().getArgument();
		    curr.getBlock().getHole().setRange(block_start, block_start + memory_needs - 1);

		    // create a new block with the rest of memory we don't need
		    // notice curr.getBlock().getHole().getEnd() was changed by line 155
		    if (curr.getBlock().getHole().getEnd() < end) {
			BlockNode newBlock = new BlockNode(
				new Block(null, new Hole(curr.getBlock().getHole().getEnd() + 1, end)), curr.getNext());

			curr.setNext(newBlock);
		    }
		    size++;
		    return true;
		}
		curr = curr.getNext();
	    }
	    return false;
	}
    }

    //best fit
    public boolean bestFitInsert(Process process) {
        Block block = new Block(process);
        BlockNode curr = start;
        BlockNode bestNode = null;
        int idealSize = Integer.MAX_VALUE;

        // Go through the blocks to find the best fit
        while (curr != null) {
            if (curr.getBlock().canPlace(block.getProcess()) && curr.getBlock().getSize() < idealSize) {
                bestNode = curr;
                idealSize = curr.getBlock().getSize();
            }
            curr = curr.getNext();
        }

        // If a suitable block was found then place the process
        if (bestNode != null) {
            int end = bestNode.getBlock().getHole().getEnd();
            bestNode.getBlock().setProcess(block.getProcess());
            int memoryNeeds = block.getProcess().getArgument();
            int blockStart = bestNode.getBlock().getHole().getStart();
            bestNode.getBlock().getHole().setRange(blockStart, blockStart + memoryNeeds - 1);

            // If there is remaining space in the block then create a new block for it
            if (bestNode.getBlock().getHole().getEnd() < end) {
                BlockNode newBlock = new BlockNode(
                    new Block(null, new Hole(bestNode.getBlock().getHole().getEnd() + 1, end)), bestNode.getNext());
                bestNode.setNext(newBlock);
            }
            size++;
            return true;
        }
        return false;
    }
    
    





    /**
     * This method goes through current memory blocks. If blocks are next to each
     * other and free it will join the blocks together making a larger block.
     */
    public void joinBlocks() {
	BlockNode ptr = start;

	while (ptr.getNext() != null) {

	    BlockNode next = ptr.getNext();

	    if (ptr.getBlock().getProcess() == null && next.getBlock().getProcess() == null) {
		int start = ptr.getBlock().getHole().getStart();
		int end = next.getBlock().getHole().getEnd();
		ptr.getBlock().getHole().setRange(start, end);
		ptr.setNext(next.getNext());
		size--;
		continue;
	    }
	    ptr = ptr.getNext();
	}
    }

   //This method gets the external fragmentation of the current memory blocks
    public int externalFragmentation() {
	BlockNode ptr = start;
	int externalFragmentation = 0;
	int totalFreeSpace = 0;
    int largestFreeBlock = 0;
     while (ptr != null) {
         if (ptr.getBlock().available()) {
             int blockSize = ptr.getBlock().getHole().getSize();
             totalFreeSpace += blockSize;
             if (blockSize > largestFreeBlock) {
                 largestFreeBlock = blockSize;
             }
         }
         ptr = ptr.getNext();
     }
     externalFragmentation = totalFreeSpace - largestFreeBlock;
     

	return externalFragmentation;
    }
    

    /**
     * This method goes through the blocks of memory and de-allocates the block for
     * the provided process_number
     * 
     * @param process_number Process to be de-allocated.
     */
    public void deallocateBlock(int process_number) {

	BlockNode ptr = start;
	while (ptr != null) {

	    if (ptr.getBlock().getProcess() != null) {
		if (ptr.getBlock().getProcess().getReference_number() == process_number) {
		    ptr.getBlock().setProcess(null);
		    joinBlocks();
		    return;
		}
	    }
	    ptr = ptr.getNext();
	}
    }
    
    
    public void compactMemory() {
        List<Process> processes = new ArrayList<>();
        BlockNode curr = start;

        // Collect all processes
        while (curr != null) {
            if (!curr.getBlock().available()) {
                processes.add(curr.getBlock().getProcess());
            }
            curr = curr.getNext();
        }

        // Reset the memory
        start = null;
        end = null;
        size = 0;

        int lastEnd = 0;
        for (Process proc : processes) {
            int memoryNeeds = proc.getArgument();
            Block block = new Block(proc, new Hole(lastEnd, lastEnd + memoryNeeds - 1));
            insertAtEnd(block);
            lastEnd += memoryNeeds;
        }

        // Add a large free block if there is remaining space
        if (lastEnd < TOTAL_BYTES) {
            Block freeBlock = new Block(null, new Hole(lastEnd, TOTAL_BYTES - 1));
            insertAtEnd(freeBlock);
        }
        joinBlocks();
    }
    
    public void insertAtEnd(Block block) {
        BlockNode nptr = new BlockNode(block, null);
        size++;
        if (start == null) {
            start = nptr;
            end = start;
        } else {
            end.setNext(nptr);
            end = nptr;
        }
    }


    /**
     * This method prints the whole list of current memory.
     */
    public void printBlocks() {
	System.out.println("Current memory display");
	BlockNode ptr = start;
	while (ptr != null) {
	    ptr.getBlock().displayBlock();
	    ptr = ptr.getNext();
	}
    }

}
