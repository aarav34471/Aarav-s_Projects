# Unix Command Pipeline and Memory Management

This Java project explores two operating-system concepts: composable command pipelines and contiguous-memory allocation.

## Command Pipeline

`commandpipeline.CommandPipeline` implements a small interactive shell for a constrained command set:

- `cat` reads a text file;
- `cut` extracts delimited fields;
- `sort` orders records;
- `uniq` removes adjacent duplicates;
- `wc` reports aggregate counts;
- `|` passes one command's output to the next.

The implementation parses a pipeline into stages and represents intermediate output as lists of strings, making the data flow explicit without spawning native processes.

## Memory Allocation Simulator

`memorymanagement.MemoryManagementSimulator` reads allocation/deallocation requests from `task-b.csv` and simulates a 1,024-byte contiguous memory space. A linked block structure supports:

- first-fit allocation;
- best-fit allocation;
- deallocation;
- external-fragmentation measurement;
- compaction after an allocation failure.

## Running

Requirements: Java 17 and Maven.

```bash
mvn clean package
java -cp target/classes commandpipeline.CommandPipeline
java -cp target/classes memorymanagement.MemoryManagementSimulator
```

Run the second command from the project directory so `task-b.csv` is available. `task-a.csv` provides sample input for command-pipeline experiments.

## Limitations

- The command parser intentionally supports only a small syntax and does not implement quoting, escaping, redirection, or native processes.
- The memory simulator models a fixed-size contiguous allocator rather than paging or virtual memory.
- Invalid input handling is intentionally lightweight.
