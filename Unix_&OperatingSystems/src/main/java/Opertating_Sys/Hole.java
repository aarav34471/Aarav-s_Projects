package taskB;

/**
* This class serves the purpose of storing the size of the block in memory.
*/
public class Hole {



	// base and limit values
	private int start;
	private int end;

	/**
	 * Default constructor.
	 * Sets the first hole the size of the maximum space, and is free.
	 */
	Hole(){
	    start = 0;
	    end = TaskB.TOTAL_BYTES-1;
	}

	/**
	 * Constructor of hole.
	 * @param start start byte of the hole.
	 * @param end end byte of the hole.
	 */
	Hole(int start, int end){
	    this.start = start;
	    this.end   = end;
	}

	public int getStart(){
	    return this.start;
	}
	 
	public int getEnd(){
	    return this.end;
	}
	
	/**
	 * This method returns the size of the hole.
	 * @return hole size
	 */
	int getSize(){
	    return (end - start) + 1;
	}

	/**
	 * This method sets the range of the hole for the block
	 * @param start start byte of the hole
	 * @param end end byte of the hole
	 */
	public void setRange(int start, int end){
	    this.start = start;
	    this.end   = end;
	}


}
