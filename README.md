# RTags Plugin for Sublime Text 3
This plugin aims to give powerful C++ navigation and modification abilities, by intergrating [RTags](https://github.com/Andersbakken/rtags) with [Sublime Text 3](https://www.sublimetext.com/) editor.

In short, RTags is a client/server application which parses C/C++ code and allows __semantic__ auto-completion, navigation, and refactoring. It is the best open-source tool I've found for C/C++ parsing, and it greatly outperforms CTags/GTags etc...

----

- [RTags Plugin for Sublime Text 3](#rtags-plugin-for-sublime-text-3)
  - [Currently Available Features](#currently-available-features)
- [Installation Instructions](#installation-instructions)
    - [Installing the Plugin](#installing-the-plugin)
    - [Installing RTags](#installing-rtags)
    - [Setting up RTags to work for the first time](#setting-up-rtags-to-work-for-the-first-time)
- [Using the Plugin](#using-the-plugin)
- [Contributions](#contributions)
- [Worth Noting](#worth-noting)

----

### Currently Available Features
- GoTo Definition/Decleration
  ![Live Usage Example of GoTo Definition/Declaration](https://github.com/papadokolos/RTags/blob/master/GIF%20Examples/goto-definition.gif)
- Find All References
  ![Live Usage Example of Find All References](https://github.com/papadokolos/RTags/blob/master/GIF%20Examples/find-all-references.gif)
- Find Overrides of Virtual Method
- Load Compilation Database

All features are available in the _Command Panel_ (via <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>), and are assigned with default key bindings (found in _Default.sublime-keymap_).

## Installation Instructions
#### Installing the Plugin
Clone this repository into your packages folder.
   
For example, within an Ubuntu machine:
```bash
cd ~/.config/sublime-text-3/Packages
git clone https://github.com/papadokolos/RTags.git
```

But wait! The plugin requires RTags in order to work, so please proceed to the next section.

#### Installing RTags
This should be fairly quick and easy. But in case you face any difficulties, feel free to ask me for help.

1. Install _Clang_ and _CMake_, which are depdendencies of RTags (See [Here](https://github.com/Andersbakken/rtags#installing-rtags))

   For example, within an Ubuntu machine:
   ```bash
   sudo apt-get install clang
   sudo apt-get install cmake
   ```
2. Install RTags

   For example, within an Ubuntu machine:
   ```bash
   cd ~/Downloads
   git clone --recursive https://github.com/Andersbakken/rtags.git
   cd rtags
   mkdir build
   cd build
   cmake ..
   make
   sudo make install
   ```
   For more information, please refer to [RTags README](https://github.com/Andersbakken/rtags#installing-rtags)

#### Setting up RTags to work for the first time
Now that you have RTags installed, it is time to use it to parse your code. A full guide can be found in [RTags' README](https://github.com/Andersbakken/rtags#setup), but basically it sums up to three steps:
1. Execute RTags server by opening a terminal and simply executing the command `rdm`.
2. Generate a [compilation databse](https://clang.llvm.org/docs/JSONCompilationDatabase.html) for your code. This file informs RTags how you build your code.

   - If you build using _CMake_:
     ```bash
     cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=1 .
     ```
   
   - If you build using _Make_:
     ```bash
     sudo apt-get install bear  # Install a helper tool
     make -c                    # Clear past builds history in order to make a full build
     bear make                  # Build the code and generate the compilation database
     ```
     
    - If you build using _SCons_:
     ```bash
     sudo apt-get install bear  # Install a helper tool
     scons -c                   # Clear past builds history in order to make a full build
     bear scons                 # Build the code and generate the compilation database
     ```
3. Direct RTags server to your generated compilation database by executing `rc -J` in the directory of the generated database.

## Using the Plugin
First, make sure that the RTags server is up and running for this plugin to communicate with it. This can be done by opening a terminal and simply executing the command `rdm`. Make sure to keep this terminal open!

Now you are free to open the _Command Panel_ (via <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>) and type `RTags:`. This will present you with all the available commands.

In case nothing happenes when you execute a command, try looking at the status bar for an error message of the plugin. For more verbose information, refer to Sublime Text's console (via <kbd>Ctrl</kbd>+<kbd>\`</kbd>). If you're still unable to solve your problem, please open an issue and I'll be glad to assist you.

## Contributions
You are very welcome to ask, suggest and contribute in any way you'd like. I'm using this plugin on a daily basis, so I'll be glad for any suggested improvements :wink:

## Worth Noting
This plugin was originally developed for my own use, and I was encouraged by my co-workers to post it to the public. Knowing that this plugin is very similar to ones that are already available via _Package Control_, especially [Sublime RTags](https://github.com/rampage644/sublime-rtags), I have no will to compete with them. So I will keep this plugin outside of _Package Control_.
