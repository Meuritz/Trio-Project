---

# Trio: A Socket Card Game!

This game is inspired by a real-life card game named **Trio**, created by Kaya Miyano. I developed this game to gain practical experience with socket programming.

---

## Requirements
- **Python 3.13.1**
- **Termcolor 2.5.0**

---

## Features
- 3-player gameplay
- Cross-platform compatibility

---

## Known Issues
- Input validation is incomplete: Be sure to enter the correct card index while playing, or the game will crash.
- If the game fails due to firewall or network issues, try using a VPN like Radmin.

---

## How to Play

1. **Install Dependencies**  
   Install **Termcolor (2.5.0)** and **Python 3.13.1** (or later) on both the server and client machines.  

2. **Set Up the Server**  
   - Start the server and bind it to a valid IP address.  
   - To do this, edit the server file and replace `"localhost"` with the desired IP address.  

3. **Connect the Clients**  
   - Open the client application.  
   - Choose the first option and follow the instructions.  
   - If the server is bound correctly and the firewall doesn’t block connections, you will successfully join the game!

---
## Extra info
- the `start.bat` file, opens one instance of the server and tree of the client, this can be used to test if the game works on the current machine
- the `3client.bat` file inside the client folder, opens 3 instances of a client, this was mainly used to test the game on different Network/Machines
---

## Authors
- [Meuritz](https://github.com/Meuritz)

[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)

---


