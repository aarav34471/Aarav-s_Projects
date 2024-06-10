


#include <stdio.h>
#include <string.h>
#include <time.h>
#include "pico/stdlib.h"
#include "includes/seven_segment.h"

#define BUTTON_PIN			16	// Pin 21 (GPIO 16)

int main() {
	bool buttonPressed, buttonPrevPress, buttonStatus, validMatch = false; //booleans names refer to the condition they hold, validMatch will be explained later
	int timeStart, timeEnd, timeDuration, timeNotPressed = 0; //integer values that hold what their names say, time duration is the duration of the button pressed
	int position = 0; //position that will be used for adding dots and dashes to binaryVals array
	bool decoding = false; //while loop boolean allows us to run and exit the second level while loop and reset values

	stdio_init_all();
	gpio_init(BUTTON_PIN);
	gpio_set_dir(BUTTON_PIN, GPIO_IN);
	gpio_pull_down(BUTTON_PIN); //pull down the button pin towards ground

	// Initialise the seven segment display.
	seven_segment_init();

	// Turn the seven segment display off when the program starts.
	seven_segment_off();



	gpio_init(SEGMENT_G); 
	//initialize middle segment
    gpio_set_dir(SEGMENT_G, GPIO_OUT); 
	//turn on middle segment for 1500 milliseconds then turn off
    gpio_put(SEGMENT_G, false);
    sleep_ms(1500); 
    gpio_put(SEGMENT_G, true); 

	printf("Welcome to the Binary Decoder\n"); //Welcome message

	char binaryVals[6] = {'\0', '\0', '\0', '\0','\0', '\0'}; //Array that holds the dots and dashes inputted by user
	//reference to index for trasnlation of binary to letter
	char *binaryDict[] = {".-", "-...", "-.-.", "-..", ".", "..-.", "--.", 
						"....", "..", ".---", "-.-", ".-..", "--", "-.", "---", 
						".--.", "--.-", ".-.", "...", "-", "..-", "...-", ".--", "-..-", "-.--", "--.."}; 
						
	while (true) {
		position = 0; //reset position value
		validMatch = false; //reset validMatch value

		//reset all values of the array
		for (int i = 0; i < 5; ++i) {
			binaryVals[i] = '\0';
		}
		//starts when button is pressed initally, variable isn't resetted
		if (gpio_get(BUTTON_PIN)){
			decoding = true;
		}
		while(decoding) {
			buttonPressed = gpio_get(BUTTON_PIN); //check for input of button
			//check if button is pressed, buttonPrevPress allows us to specify condition in the following
			if (buttonPressed && !buttonPrevPress) {
			timeStart = clock(); //puts the exact time into the variable timeStart
			buttonPrevPress = true;
		}
			//if button is not pressed only if the button was pressed previously
			else if (!buttonPressed && buttonPrevPress) {
			timeEnd = clock(); //puts the exact end time into timeEnd
			buttonPrevPress = false;
			timeDuration = ((timeEnd - timeStart)*1000)/CLOCKS_PER_SEC; //calculates difference in time in milliseconds
			timeStart = clock(); //starts a new timer when button is not pressed
			//if the entries are more than 4 dashes/dots its invalid
			if (position > 4) { 
				printf("Error: Binary Limit Reached\n");
				seven_segment_show(26);
				sleep_ms(1500);
				seven_segment_off();
				decoding = false; //allow while loop to finish and reset all values
				break;
			}
			//if the press is longer than 700 milliseconds its invalid
			if (timeDuration > 700) {
				printf("Error: Time Limit Reached\n");
				seven_segment_show(26);
				sleep_ms(1500);
				seven_segment_off();
				decoding = false;
				break;
			}
			//or else if the press is longer than 250 milliseconds a dash is added to the array
			else if (timeDuration > 250) {
				//adding dash to the index of the array then add one to index variable
				binaryVals[position++] = '-';
			}
				//or else if the press is  than 250 milliseconds a dash is added to the array
			else {
				//adding dot to the index of the array then add one to index variable
				binaryVals[position++] = '.';
			}
		}
			//When button isn't pressed
			if (!buttonPressed) {
				timeEnd = clock(); //time end for button Not Being Pressed
				timeNotPressed = ((timeEnd - timeStart)/CLOCKS_PER_SEC)*1000; //calculate how long not pressed for
				//if not pressed more than 400 milliseconds then convert array of binary into letter
				if (timeNotPressed > 400) {
					char binaryStr[5] = ""; //create empty string
					strcat(binaryStr, binaryVals); //concatenate the array into the empty string
					for (int i = 0; i < 26; i++) {
						//loop through the binary dictionary and check if the binary pattern matches any binary code
						if (strcmp(binaryStr, binaryDict[i]) == 0) {
							printf("%s = ", binaryStr); //print binary pattern
							validMatch = true; //change value of boolean validMatch to true
							char letter = 'A' + i; //aschii format of displaying letter using the value of i in the loop 
							printf("%c\n", letter); //print the letter
							seven_segment_show(i); //run the seven segment method and display the letter on the seven segment
							sleep_ms(1500); //wait 1500 milliseconds
							seven_segment_off(); //turn off the seven segment
							decoding = false; //allowing to exit the while loop
							break; //break from the for loop
						}
						
					}
					//check if the there hasn't been any matches with 
					if (!validMatch) {
							printf("Error: Invalid Binary Input\n"); 
							seven_segment_show(26); //show 8 on the seven segment display
							sleep_ms(1500); 
							seven_segment_off();
							decoding = false; //finish the while loop
							break;
						}
				}
			}
	}
	}
return 0; //finish function
}


