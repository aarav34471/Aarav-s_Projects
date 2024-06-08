package taskB;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

/**
 *
 * Main function for memory management.
 */
public class TaskB {

    // size of memory
    public static final int TOTAL_BYTES = 1024;

    /*
     * The first number is the reference id of job. The second number is a request
     * to allocate or deallocate. (1 - Allocate, 2 - Deallocate) The third number if
     * allocate will try and allocate those amount of bytes into a memory stack of
     * 1024 bytes. If it is deallocate, the third argument will be the reference id
     * to deallocate from memory.
     * 
     * NOTE: you should read the process input from taskB.txt instead of putting it
     * in the Java file
     */
   
    // Keep track of all processes created
    private static ArrayList<Process> listof_processes;
    private static String filename = "taskB.csv";

    public static void createProcesses() {
    	listof_processes = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] values = line.split(",");
                int refNum = Integer.parseInt(values[0].trim());
                int operation = Integer.parseInt(values[1].trim());
                int argument = Integer.parseInt(values[2].trim());
                listof_processes.add(new Process(refNum, operation, argument));
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    //first fit
    private static void firstFit() {

        MainMemory manager = new MainMemory();
        manager.insertAtStart(new Block());

        for (Process process : listof_processes) {

            if (process.isAllocating()) {
                boolean placed = manager.firstFitInsert(process);
                // externalFragmentation has been implemented
                
                if(!placed) {
                    System.out.println("Request " + process.getReference_number() +
                        " failed at allocating " + process.getArgument() + " bytes." );
                    System.out.println("External Fragmentation is " +
                        manager.externalFragmentation() + " bytes."); // memory print
                    manager.printBlocks();
                    // Compact memory after allocation failure
                    System.out.println("------ After Compaction ------");
                    manager.compactMemory();
                    manager.printBlocks();
                    
                    return;
                }
            } else if (process.isDeallocating()) {
                manager.deallocateBlock(process.getArgument());
            }
        }
        System.out.println("Success");
        // memory print
        manager.printBlocks();
    }


    //best fit
    private static void bestFit() {

        MainMemory manager = new MainMemory();
        manager.insertAtStart(new Block());

        for (Process proc : listof_processes) {

            if (proc.isAllocating()) {
                boolean placed = manager.bestFitInsert(proc);
                if (!placed) {
                    System.out.println("Request " + proc.getReference_number() + " failed at allocating "
                            + proc.getArgument() + " bytes.");
                    System.out.println("External Fragmentation is " + manager.externalFragmentation() + " bytes.");
                    // memory print
                    manager.printBlocks();
                    // Compact memory after  failure
                    System.out.println("------ After Compaction ------");
                    manager.compactMemory();
                    manager.printBlocks();
                    return;
                }
            } else if (proc.isDeallocating()) {
                manager.deallocateBlock(proc.getArgument());
            }
        }
        System.out.println("Success");
        // memory print
        manager.printBlocks();
    }


    public static void main(String[] args) {

	createProcesses();

	System.out.println("----------First Fit---------");
	firstFit();

	System.out.println("----------Best Fit---------");
	bestFit();

    }

}
