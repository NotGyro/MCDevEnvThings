#!/usr/bin/python

import sys
import subprocess
import getopt
import pathlib
import os.path
import platform
from pathlib import Path

sys.path.append(str(Path(".").absolute()))

from devenvhackery import makelink

slash = "/"
if(platform.system() == "Linux"):
    slash = "/"
elif(platform.system() == "Windows"):
    slash = "\\"

def usage():
    print("""devenv-hackery.py <mod directory>
Treats this as a source directory by default.
Options:
-t <target (forge) directory> sets Forge directory (optional)
-v verbose flag (optional)""")

def main():
    #Copy our argument list.
    elimination = sys.argv[1:]
    try:
        #Use GNU-style arguments so option and
        #non-option arguments can be dealt with.
        opts, args = getopt.gnu_getopt(sys.argv[1:], "vht:", ["targetdirectory="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    newdir = None
    verbose = True
    isGradle = True

    #Poll options.
    for o, a in opts:
        if(o in elimination):
            elimination.remove(o)
        if(a in elimination):
            elimination.remove(a)
        if( o == "-h"):
            usage()
            sys.exit()
        elif( o in ("-v", "--verbose") ):
            verbose = True
        elif( o in ("-t", "--directory") ):
            newdir = a

    errcode = 1
    forgename = "forgedir"
    if(isGradle):
        forgename += "-1.7.2"
    forgename += ".txt"
    #Get our Forge directory.
    fileexists = os.path.isfile(forgename)
    if((not fileexists) and (newdir == None)):
        print("Error: attempting to use devenv hackery without Forge dir set!")
        sys.exit(errcode) #Exit with an error code.
    file = ""
    if(not fileexists):
        file = open(forgename, mode="x")
    else:
        file = open(forgename, mode="r+")

    forgepath = None;
    if(not (newdir == None)):
        file.truncate()
        file.write(newdir)
        forgepath = newdir
        if(verbose):
            print(forgename + " overwritten with: " + newdir)
    else:
        forgepath = file.readline()
        if(verbose):
            print("Forge path set by " + forgename + " to: " + forgepath)
    file.close()

    #Figure out what our mod directory is.
    moddir = None
    if(not (len(elimination) == 1)):
        print("Error: too many anonymous options or no mod selected!")
        sys.exit(errcode) #Exit with an error code.
    else:
        moddir = elimination[0]

    #Print some info
    if(verbose):
        print("Mod directory set to: " + moddir)
        if(newdir != None):
            print("Forge directory set by option to: " + newdir)
    modPath = Path(moddir)
    
    modname = str(modPath.absolute()).rpartition(slash)[2]
    pathfinal = forgepath + slash + modname
    if not (Path(pathfinal).exists()):
        makelink(pathfinal,str(modPath.absolute()))
    #else:
        #os.remove(pathfinal)
        #makelink(pathfinal,str(modPath.absolute()))
    
    file = open(forgepath.rpartition(slash)[0] + slash + "settings.gradle", mode="r+")
    #Jump to the end of the file.
    file.seek(0, 2)
    file.write(", '" + modname + "'")
    

if __name__ == "__main__":
    main()
