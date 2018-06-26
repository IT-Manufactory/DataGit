# Database collaboration tool
This library is aimed to provide better collaboration amongst the team. 

## Installation

### Requirements
The library is programmed in python. It uses `virtualenv` and `pip`.

(Please use GitBash on windows and standard Terminal on Mac or Linux)

* Python version 3.6 
    - **UNIX/LINUX**
        - Install it using Homebrew. Use `brew install python3`.
        - Make sure `python3 --version` prints version greater than 3.3
    - **Windows**
        - Install it using the official python installer. Click [here](https://www.python.org/ftp/python/3.6.5/python-3.6.5-amd64.exe) to download installer.
        - After the ionstallation has been done. Rerun the installer. Select Add Componenets and then check pip, and create environment variables and run the installer again.
        - Make sure `python --version` prints a version greater than 3.3 
* `pip` 
    - Comes with Python installer on windows. 
    - Use `sudo easy_install pip` to install it on mac 
* `virtualenv` 
    - Use `pip install virtualenv` to install it through terminal or Git Bash

* `make`
    - **Unix/Linux** Comes preinstalled.
    - **Windows** 
        - Download the zip file from [this](https://sourceforge.net/projects/ezwinports/files/make-4.2.1-without-guile-w32-bin.zip/download) link.
        - Extract the contents of the zip.
        - Copy the contents to `C:\Git\ming64\`. Merging the folders. **DO NOT** overwrite/replace anything.
        - Restart Git Bash.


## How does the tool work?

There are three different folders named `mac`, `windows` and `linux`. Because Oracle needs specific drivers for each operating system, they has to be in different folders. These folder therefore, contains the respective drivers and the `run.py` script, to run the sql scripts.

Another folder named **db** should contain two child folders, **init** and **additions**. If this is not present in your `da-database` directory, please create them, otherwise the script will throw an error, after not finding those folders.

So your final directory structure should look like this:
```
da-database
│   README.md
│   Makefile
│   requirements.txt
│   connection.ini
│   .gitignore
│───db
│   │───init
│   └───additions
│───mac
│───windows
└───linux
```

### Install python tool
Next step is to install the tool. In order to do this, run `make install` (on mac/linux)/ `make wininstall` (on windows). This will install the python project dependencies in the folder. The new folder structure should look like this:

```
da-database
│   README.md
│   Makefile
│   requirements.txt
│   connection.ini
│   .gitignore
│───db
│   │───init
│   └───additions
│───mac
│───windows
│───linux
└───venv

```
Finally run the following command in terminal/GitBash:

`git update-index --assume-unchanged connection.ini`

This is to make sure that the main connection string file stays in your local repo, even when you change the credentials. (Because this file should be unique to each user)


### Run the tool

When the `make install`/`make wininstall` command is run successfully, you should be able to run `make run`/`make winrun`/`make linuxrun` command through terminal/GitBash. 

- The program first looks for connection string. This should be provided in **connection.ini** file. An example connection string is provided below:

      
        [Database]
        url = localhost
        port = 1521
        username = testuser
        password = sales
        service = xe
        
- Next the program will look for SQL files in folder `db/init/`. The files will be arranged in the increasing order and executed. You can place all the SQL scripts in this folder which you want to run before any other scripts in the additions folder.

- Finally the program will look for SQL files in folder `db/additions/`. The files will be arranged in a similar fashion as `init` folder.
- The scripts saves the files it last ran in the `connection.ini` file. So next time when a new script is added, it will only run the new files and not the previous files.

### Placing SQL files in the repository

In order to collaborate the database changes with other team members effectively, please follow the following set of conditions while creating and placing new files in the repo:

- **`init`** folder should only contain initialization scripts. All SQL files that contain addtions (or removals, alters etc) should be placed in **`additions`** folder.
- Use only sql files. `.dmp` files are not yet supported.
- SQL statements in each file should be separated using a **semincolon `:`**. **`/`** is not supported as it causes problems with string splitting between the sql statements and actual database entry strings.
- **Use proper naming convention for the files**: 
    -  In order for your SQL scripts to work properly, the files should be named as follows:
        - **YYYYMMDDHHMMSS.sql**. This uses the year, month, day and time (24H format) the file was created. The last "seconds" part (SS) is  for your convenience. Use it to provide the scripts in the order you want them to run. 
        - eg. Three SQL files created on 27th March, 2018, at 01:35 PM should be named like: 20180327133501.sql, 20180327133502.sql, 20180327133503.sql.
        - eg. Just one file created on 27th March, 2018, at 01:35 PM should be named like: 20180327133500.sql
    
- Once you commit and push qn SQL file. **Do not make any changes in that file.** It is possible that others may have already used that file on their system and any changes you make will not be executed on their system.
## 

**That's it. The tool should run without problems. Support for postgreSQL will be added once we all make the switch.**

**In case of any problems or suggestions, feel free to contact me [Varij Kapil](mailto:varij.kapil@it-manufactory.com)** 