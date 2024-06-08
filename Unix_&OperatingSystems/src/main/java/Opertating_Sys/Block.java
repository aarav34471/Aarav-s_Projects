package taskB;


/**
* This class serves the purpose of simulating a block in memory,
* storing the process accessing that memory, and size of the memory hole.
*/
public class Block {


	// Process and size of memory hole
	// Look at the end of this file for the definition of Hole
	private Process proc;
	private Hole hole;


	// Default constructor with maximum memory allocation
	public Block(){
		proc = null;
		hole = new Hole(); 
	}

	/**
	 * Constructor for Block
	 * @param proc Process, null if available.
	 * @param hole used to show or give size of memory for this current block
	 */
	public Block(Process proc, Hole hole){
		this.proc = proc;
		this.hole = hole;
	}

	/**
	 * Constructor for block, only given a process, to set size of hole later if need be.
	 * @param proc Process, null if no job and is free.
	 */
	public Block(Process proc){
		this.proc = proc;
	}

	/**
	 * If the Process proc for the current block is null, then the block is available.
	 * @return True if block is available, false if not.
	 */
	public boolean available(){
		return proc == null;
	}

	/**
	 * This method checks to see if the current Process proc wanting to be placed can be placed at this block.
	 * If the block is available and the proc is allocating and the bytes to be placed are within this blocks size
	 * then it can be placed.
	 *
	 * @param proc Process to check if can be placed at this block
	 * @return True if it can be placed, false if it cannot.
	 */
	public boolean canPlace(Process proc){
		return available() && proc.isAllocating() && proc.getArgument() <= getSize();
	}

	/**
	 * This method is a setter for the Process in this block.
	 * Set null to free block, or adding Process to the block.
	 * @param j Job to be set.
	 */
	public void setProcess(Process proc){
		this.proc = proc;
	}

	/**
	 * Getter for the Process in this block.
	 * @return current proc, null if no process.
	 */
	public Process getProcess(){
		return this.proc;
	}

	/**
	 * This method gets the hole for this block.
	 * @return hole
	 */
	public Hole getHole(){
		return this.hole;
	}

	/**
	 * This method displays the current block and what is allocated to it if it is allocated.
	 */
	public void displayBlock(){

		int start = hole.getStart();
		int end   = hole.getEnd();

		String allocated = "free";

		if(!available()) {
			allocated = "allocated to Process " + proc.getReference_number();
		}

		System.out.printf("[%d-%d): %s\n",start,end+1,allocated);
	}


	/**
	 * This method returns the size of the hole for the block.
	 * @return hole size
	 */
	public int getSize(){
		return hole.getSize();
	}


}

