package taskA;

import java.io.*;
import java.util.*;

public class TaskA {

    public static void main(String[] args) {
    	
    String commandLine;

    System.out.println("Operating Systems Coursework");
    System.out.println("Name: Aarav"); // display your name in here
    System.out.println("Please enter your commands - cat, cut, sort, uniq, wc or |");
	
    BufferedReader console = new BufferedReader (new InputStreamReader(System.in));
	
    while (true) {
        System.out.print(">> ");
        try {
            commandLine = console.readLine();
            if (commandLine == null || commandLine.trim().isEmpty()) {
                continue;
            }
            commandProcess(commandLine);
            //commandProcess(commandLine);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    }
	
    public static void commandProcess(String inputCommand) {
		
        String[] parts = inputCommand.split("\\|");
        List<String> output = null;
		
        for (String part: parts) {
            part = part.trim();
            String[] command = part.split(" ");
            String cmd = command[0];
			
            switch (cmd) {
                case "cut":
                    int field = -1;
                    String delimiter = ",";
                    if (command.length >= 5 && command[1].equals("-f") && command[3].equals("-d")) {
                        delimiter = command[4];
                        field = Integer.parseInt(command[2]) - 1; // 1-based to 0-based
                        output = cut(output, field, delimiter);
                    } else if (command.length >= 3 && command[1].equals("-f")) {
                        field = Integer.parseInt(command[2]) - 1; // 1-based to 0-based
                        output = cut(output, field, delimiter);
                    } else {
                        System.out.println("Invalid cut command");
                    }
                    break;
                case "cat":
                    if (command.length < 2) {
                        System.out.println("Invalid cat command");
                        break;
                    }
                    String fileName = command[1];
                    try {
                        output = cat(fileName);
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                    break;
                case "sort":
                    output = sort(output);
                    break;
                case "uniq":
                    output = uniq(output);
                    break;
                case "wc":
                    boolean lines = command.length > 1 && command[1].equals("-l");
                    System.out.println("Count = " + wc(output, lines));
                    return;
                default:
                    System.out.println("Unknown command: " + cmd);
                    return;
            }
        }
        if (output != null) {
            output.forEach(System.out::println);
        }
    }
		
    public static int wc(List<String> input, boolean linesOnly) {
    	    if (linesOnly) {
    	        return input.size();
    	    }
    	    int words = 0;
    	    int bytes = 0;
    	    for (String lines: input) {
    	        words = words + lines.split("\\s+").length;
    	        bytes = bytes + lines.getBytes().length;
    	    }
    	    return words + bytes;
    	}

    public static List<String> cat(String filename) throws IOException {
        List<String> output = new ArrayList<>();
        String line;
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            while ((line = reader.readLine()) != null) {
                output.add(line);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return output;
    }

    public static List<String> cut(List<String> input, int field, String delimiter) {
        if (input == null) {
            System.out.println("No input provided");
        }
        if (field == -1) {
            System.out.println("Field not inputted");  
        }
        
        List<String> output = new ArrayList<>();
        for (String line : input) {
            String[] fields = line.split(delimiter.substring(1, delimiter.length()-1));
            if (fields.length > field) {
                output.add(fields[field]);
            } else {
                output.add("");
            }
        }
        return output;
    }

    public static List<String> sort(List<String> input) {
        if (input == null) {
            System.out.println("No input provided");
            return Collections.emptyList();
        }
        List<String> sortedList = new ArrayList<>(input);
        Collections.sort(sortedList);
        return sortedList;
    }

    public static List<String> uniq(List<String> input) {
        if (input == null) {
            System.out.println("No input provided");
        }
        List<String> output = new ArrayList<>();
        String prev = null;
        for (String word : input) {
            if (!word.equals(prev)) {
                output.add(word);
                prev = word;
            }
        }
        return output;
    }
}
