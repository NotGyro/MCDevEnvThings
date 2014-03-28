#!/usr/bin/python

import sys
import subprocess
import getopt
import pathlib
import os.path
import platform
from pathlib import Path

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
-v verbose flag (optional)
-a assets-only mode flag (optional)
-g Use Gradle paths.""")

def makelink(alias, source, verbose=True):
    if not (Path(alias).exists()):
        #Make a symlink.
        first = ""
        second = ""
        cmd = ""
        if(platform.system() == "Linux"):
            #Todo
            first = source
            second = alias
        elif(platform.system() == "Windows"):
            first = alias
            second = source
            cmd = "mklink /J"
        if(verbose):
            print(subprocess.check_output(cmd + " " + first + " " + second, shell = True))
        else:
            subprocess.call(cmd + " " + first + " " + second, shell = True)

#Cluttered because I was totally overengineering this.
def retrieveModPackageNames(pathname):
    p = Path(pathname)
    #Get all Java files below our path.
    sources = list(p.glob("**/*.java"))
    output = []
    for srcPath in sources:
        with srcPath.open() as srcFile:
            #package zettabyte.weirdscience;
            for line in srcFile:
                #Extract package name from line if present.
                package = line.partition("package ")[2].partition(";")[0]#.partition(".")[0]
                use = True
                if(package == ""):
                    use = False
                if(package in output):
                    use = False
                if(not (";" in line)):
                    use = False
                if(use):
                    output.extend([package])
                    break
    #Eliminate child packages.
    finaloutput = list(output)
    for package1 in output:
        for package2 in output:
            if(package1 in package2) and (not (package1 == package2)):
                #output.remove(package2)
                while package2 in finaloutput:
                    finaloutput.remove(package2)
            elif(package2 in package1) and (not (package1 == package2)):
                #output.remove(package2)
                while package1 in finaloutput:
                    finaloutput.remove(package1)

    #for tokill in toremove:
    #    if(tokill in output):
    #        output.remove(tokill)

    return finaloutput

#Make sure the directory hirerarchy required to make a link at a path exists. (recursive)
def ensureFolder(path):
    p = Path(path)
    p2 = Path(path.rpartition(slash)[0])
    if not p.exists():
        if not p2.exists():
            ensureFolder(str(p2.absolute()))
            os.mkdir(str(p.absolute()))
        else:
            os.mkdir(str(p.absolute()))
            
#Turn a package name into a folder name.
def dirPackageName(name):
    return name.replace(".",slash)

def main():
    #Copy our argument list.
    elimination = sys.argv[1:]
    try:
        #Use GNU-style arguments so option and
        #non-option arguments can be dealt with.
        opts, args = getopt.gnu_getopt(sys.argv[1:], "gavht:", ["targetdirectory="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    newdir = None
    verbose = True
    isAssets = False
    isGradle = False

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
        elif( o in ("-a", "--assets") ):
            isAssets = True
        elif( o in ("-g", "--gradle") ):
            isGradle = True


    if(verbose and isAssets):
        print("Setting up assets folder.")

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
    file = open("forgedir.txt", mode="r+")

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
    for p in list(modPath.glob("**/assets/*")):
        if(p.exists()):
            last = str(p).rpartition(slash)[2]
            if not(Path(forgepath+slash+"assets"+slash+last).exists()):
                makelink(forgepath+slash+"assets"+slash+last,str(p.absolute()))

    lowest = None
    lowestCount = 999
    forgepath = forgepath + "java" + slash
    if not isAssets:
        packageNames = retrieveModPackageNames(moddir)
        print(1)
        for packageName in packageNames:
            #Do the hard stuff.
            print(2)
            pFname = dirPackageName(packageName)
            for pdir in list(modPath.glob("**/" + pFname + "/*")):

                if not (pdir.is_dir()):
                    pdir = pdir.parents[0]
                print(str(pdir.absolute()))
                print(slash)
                if (str(pdir.absolute()).count("assets") == 0):
                    print(4)


                    java = list(pdir.glob("**/*.java"))
                    #Is this a folder with java files in it?
                    if(len(java) > 0):
                        if(str(pdir.absolute()).count(slash) <= lowestCount):
                            lowest = pdir
                            lowestCount = str(pdir.absolute()).count(slash)

            #create the link
            if not (lowest == None):
                pathfinal = forgepath+slash+pFname
                ensureFolder(pathfinal.rpartition(slash)[0])
                if not (Path(pathfinal).exists()):
                    print(pathfinal)
                    #make our link
                    makelink(pathfinal,str(lowest.absolute()))
                    #else:
                        #os.remove(pathfinal)
                        #makelink(pathfinal,str(pdirs.absolute()))

if __name__ == "__main__":
    main()
