My thought process in creating this python application was try to replicate as much as possible from the script
"optical_write_test.sh". For example if there was an echo or comment, I would use Python print and have the same 
comments, but I had some challenges. 
I had some troubles finding the equivalent commands from the Python libraries. If I can't find a Python library for a 
task, I opted for command line options. But since I developed this program in Windows, I used Windows commands in 
os.system and subprocess.call for powershell, example burning an image and mounting. Some areas of the code might not be
1 for 1, but it is the closest I can get. 
I tested quite a bit for the program to execute gracefully, but there might be some errors in areas that require a 
physical ROM drive because I didn't have access to one. I had to change the logic and order in those and some other 
areas, but it should behave very similarly. The eject command is untested. 
Finally, I did not overly optimize the code, and I just stuck with the requirement in replicating the script in Python.
