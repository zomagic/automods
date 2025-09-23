# automods

Purpose: AutoMods is a helper tool that automatically downloads and installs a collection <br>
of external modules for CerberusX (https://cerberus-x.com/) <br>
It works by reading a simple list of links (from a txt file) and fetching the corresponding modules. <br>
The tool then extracts them into the modules_ext (or custom) folder of your CerberusX installation. <br>

Installation
============

Copy the following files into the /bin/ folder of your CerberusX installation:
- automods.exe
- automods.txt

Why there? You might ask. <br>
To allow the app to know CerberusX location and easily copy the module in modules_ext without ask. 

Building from Source (Optional)
===============================

The source code is written in Python.
- automods.py

To compile:<br>
    pip install pyinstaller<br>
    pyinstaller --onefile --distpath . --name automods.exe automods.py<br>

Command Line Usage
==================
    automods.exe [-into=modulefolder][-update=modname,modname,...]

When execute, automods.exe reads the automods.txt file and downloads the modules listed inside.
It will also apply any default you provide when executing automods.exe with parameter

Parameters:

-into=modulefolder <br>
	Target folder name for external modules (relative to the CerberusX folder)<br>
	Without arguments (default), it will use 'modules_ext'<br>

-update=modname,modname,... <br>
	Force to update this modules and replace what in your system. <br>
	Without this command, it will skip if your system already have that module.<br>
	With arguments (comma-separated list of modname): updates only those specific modules.<br>
	use 'ALL' to updates all modules in the list.<br>
  ⚠ WARNING <br>
  Running with the -update option will replace any existing modules with the same name.<br>
  If you have modified a module for your own use, do not run with -update or your changes will be lost.<br>
  👉 To be safe, back up your customized modules before updating.<br>
  Better safe than sorry!<br>

  Example:<br>
  
      Example1: automods.exe <br>
      Downloads all modules, skipping existing ones.<br>
      Example2: automods.exe -into=my_module<br>
      Downloads all modules into a folder named my_module. <br>
      Example3: automods.exe -update=ALL<br>
      Downloads all modules and replaces any existing ones.
      Example4: automods.exe -update=diddy,fantomCX<br>
      Updates only the diddy and fantomCX modules. All others will be download but remain untouched if already there. <br>


Included Modules
================
- FantomCX - by Michael Hartlef<br>
- Flixel - by Arthur 'devolonter' Bikmullin<br>
- Vortex by Javier San Juan Cervera<br>
- Minib3d by Simon Harrison<br>
- GUIBasic by Christopher Challenger<br>
- Holzchopf<br>
- cTiled by TheMrCerebro<br>
- box2d - Physic for CerberusX<br>
- saveImage - by FantomGL<br>
- rch by Rich Pantson<br>
- crt by PixelPaladin<br>
- sdl2mixer by Ivelle Games<br>
- SimpleUI and Argyne by Nobuyuki<br>
- Diddy - by Shane Woolcock and Steven Revill<br>
- realtime by Martin Leidel<br>
- gif Loader by CopperCircle<br>
- ...and possibly others<br>
You can add or edit the module list yourself at automods.txt <br>


# Configuration File (automods.txt)

These text files define what modules to download and how to handle them.

Commands:

Use DOWNLOAD command to download a file:

    [!] DOWNLOAD = <link> , <module_name>

-This command automatic downloads and unzips a module into <module_name>.<br>
-For GitHub repos, just give the repo link (e.g., https://github.com/swoolcock/diddy).<br>
-If <module_name> is not specified, the tool uses the repo/zip name.<br>
-Add ! before DOWNLOAD to force overwrite existing modules.<br>

Use COPY or MOVE command to copy or move from folder to another folder:

    [!] MOVE = <fromFolder> , <toFolder>
    [!] COPY = <fromFolder> , <toFolder>

-Moves or copies a folder from one place to another within modules_ext. Example name: "sdl2mixer\modules_ext\sdl2mixer" , "sdl2mixer"<br>
-Add ! before COPY or MOVE to force overwrite.<br>

Use COPYC or MOVEC command to copy or move the contents from folder to another folder:

    MOVEC = <fromFolder> , <toFolder>
    COPYC = <fromFolder> , <toFolder>
	
-The above command will always replace any duplicate entry

Use DELETE command to delete a folder or a file:

    DELETE = <Folder> | <File>
    
Example:
  
    DOWNLOAD = "https://github.com/MikeHart66/fantomCX/","fantomCX"
    DOWNLOAD = "https://github.com/zomagic/guiBasic","guiBasic"
    MOVE     = "guiBasic\guiBasic" , "guiBasic"
    DOWNLOAD = "https://github.com/swoolcock/diddy"
    MOVE     = "diddy\src\diddy" , "diddy"         		
    COPY     = "diddy\src\threading" , "threading" 
    DOWNLOAD = "https://github.com/swoolcock/diddy", "diddy_temp"
    COPY     = "diddy_temp\src\diddy" , "diddy"         		
    DELETE   = "diddy_temp"	

