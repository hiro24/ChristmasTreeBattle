# ChristmasTreeBattle
The code, gerber files and 3d print files for a capture the flag style raspberry pi pico project.

![image](https://github.com/user-attachments/assets/12340b66-b73f-4f23-9d50-470fbe9b1382)

---

## Table of Contents
1. [Overview](#overview)
2. [Gerber files](#gerber-files)
3. [STL Files](#stl-files)
4. [Code](#code)
5. [Final Thoughts](#final-thoughts)
6. [Contact](#contact)

---

## Overview

These are the main files for a project I made that I called the "Christmas Tree Battle 2024". It consisted of 5 small Christmas trees with programmable LEDs attached to Raspbery Pi Picos. They would come online and talk to a central server to track what color the lights were set to. The central server would host a website that would show in real time a "score" for each color. The more trees were set to a given color, the faster that color's score would go up. The point of this was to run a capture the flag style game for a week at my office. The other co-workers seemed to enjoy it.

![image](https://github.com/user-attachments/assets/f55d6605-fa8a-436f-b8bc-35fba82bef10)


At the request of a few ppl, I'm including the sanitized files here along w/ any thoughts as they come. Hopefully that should be sufficient for you to recreate this project if you so desire.

## Gerber files

Order from your favorite vendor or print them yourself if that's your jam. I used pcbway.
* **Gerber_Christmas_Tree.zip** - This is the custom PCB designed to hold the LEDs and to plug into the control board. 
* **Gerber_Control_Board.zip** - This is the custom PCB for the base, which will hold the Raspberry Pi Pico W, 3 buttons and 3 female headers.

## STL Files

* **Tree_Back.stl** - The back of the Christmas tree
* **Tree_Front.stl** - The front of the Christmas tree
* **Tree_Peg_Support.stl** - There are a few holes in the two halves. These pegs are meant to be placed in them to add stability. I also glued the two halves together, but the pegs help.
* **tree_case_top.stl** - The top portion of the control board
* **tree_case_bottom.stl** - The bottom portion of the control board onto which the Gerber_Control_Board.zip PCB will be mounted. **NOTE:** I used melt in brass inserts to secure the board to the case with screws.

## Code

Some notes on the code:
* **pico.py** - This will become main.py on your pico. Use MicroPython. You'll need to customize a few variables, such as WIFI_CREDENTIALS, device_name and API_KEY (just make something up) as well as the API_URL which will be the IP of the server you're running on. For security, I used https and placed this behind an NGINX Proxy Manager with a LetsEncrypt cert, but those instructions are beyond the scope of this readme. You can operate this without going that far.
* **server.py** - You'll want to update the VALID_DEVICE_IDS here with the names of the devices you set in pico.py for device_name. Also, whatever you chose for an API key, you'll need to set here in API_KEY.
* **score.py** - This will be ran along with server.py. score.py will take the information from device_states.json and convert it into more meaningful scores and store that in scoreboard.json. No mondifications should be needed for this file.
* **webserver.py** - This will start a webserver on port 8000 which will serve the contents of the html directory. In here are an image as well as an html file This should read the scoreboard.json and display it in realtime.
* **🚨 🚨 🚨 IMPORTANT!!! 🚨 🚨 🚨** You will need to create a symbolic link for **scoreboard.json** in the **html** directory or the website will not read the scores!

## Final Thoughts
If you want to try to replicate this project, I'd recommend hooking everything up on a breadboard first before you begin 3D printing and ordering PCBs. As I stated earlier, for security, I would put the webserver behind an NGINX Proxy Manager with a certificate so that API traffic and webserver can be done via https. The current score.py will only track scores between 8AM - 4:30PM Monday thru Friday, but this is changeable easily enough in the while True section. 

Currently, devices will send a heartbeat every 2 minutes to the server. If the server checks scores and finds a device hasn't checked in in over 5 minutes, it will be removed from the trees. That is to say if there were 5 red trees and 1 pico went offline, 5 minutes later, give or take, that number should reduce to 4. These heartbeats/timeouts can be adjusted for tighter times. I just didn't want to flood the network w/ too much chatter. Also, when a device initially comes online its color will be "NULL" until a button is pressed.

The tree custom PCB has 3 right angle header pins soldered onto the bottom. This is how they connect to the control board. 

The LEDs used are DC5V WS2812D 8mm which I got from here: https://www.aliexpress.us/item/3256805848765212.html

Buttons are just standard buttons you get with any Raspberry Pi kit, and 3 female header pins. The pico is soldered directly onto the control board. They're cheap. It's okay. :) 

## Contact

I wish you well, o maker of trees. If you want to contact me about this project, I'll do my best to try to help you along if you're having trouble. You can reach me at: hiro24@gmail.com 
