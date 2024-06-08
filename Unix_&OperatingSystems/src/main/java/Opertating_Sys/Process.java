package taskB;

/**
 * This class defines basic aspects of a Process
 *
 */
public class Process {

    // Private variables
    private int reference_number;
    private int operation;
    private int argument;

    // Default constructor
    private Process() {
    }

    /**
     *
     * @param reference_number A reference number (a unique identifier for that
     *                         operation)
     * @param operation        An operation (either 1 for allocate? or 2 for
     *                         de-allocate?)
     * @param argument         An argument (a size in bytes for an allocate
     *                         operation; a reference number for a de-allocate
     *                         operation)
     */
    public Process(int reference_number, int operation, int argument) {
	this.reference_number = reference_number;
	this.operation = operation;
	this.argument = argument;
    }

    public int getReference_number() {
	return this.reference_number;
    }

    public int getOperation() {
	return this.operation;
    }

    public int getArgument() {
	return this.argument;
    }

    public boolean isAllocating() {
	return getOperation() == 1;
    }

    public boolean isDeallocating() {
	return getOperation() == 2;
    }

}
