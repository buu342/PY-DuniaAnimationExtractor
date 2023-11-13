# Dunia Engine Animation Extractor
# Version 0.1
# By Buu342

import os
import sys
import math
import struct


"""=============================
           Constants
============================="""

# Enable verbose prints
DEBUG = True

# Useful constants
SKIP = 16
ANIMATIONLENGTH_START = 196
SECTIONOFFSETS_START = 200


"""=============================
            Globals
============================="""

global_mabversion = 0


"""=============================
         Helper Classes
============================="""

class MABOffsets:
    """
    Stores the offset and size of each section in the MAB file
    """

    UnknownSection1: (int, int)
    UnknownSection2: (int, int)
    Rotation: (int, int)
    Keyframes: (int, int)
    UnknownSection3: (int, int)
    Offsets: (int, int)
    Events: (int, int)
    UnknownSection4: (int, int)
    UnknownSection5: (int, int)

class RotKeyFrameSection:
    """
    Stores helper information about the rotation keyframe section
    """

    OffsetStart: int
    Size: int

    def __repr__(self) -> str:
        return f"{type(self).__name__}(start={hex(self.OffsetStart)}, size={self.Size})"


"""=============================
        Parser Functions
============================="""

def GetMABVersion(file):
    """
    Reads the MAB file's header to get the version of the embedded data
    If the format is unsupported, it stops the program.
    """

    supported = False
    data = int.from_bytes(file.read(1))
    if (data == 0x4C):
        print("Far Cry 2 MAB file")
    elif (data == 0x61):
        print("Far Cry 3 MAB file")
        supported = True
    elif (data == 0x62):
        print("Far Cry 3: Blood Dragon MAB file")
    elif (data == 0x81):
        print("Far Cry 4 MAB file")
    elif (data == 0x82):
        print("Far Cry Primal MAB file")
    elif (data == 0xB0):
        print("Far Cry 5/New Dawn MAB file")
    else:
        print("Unknown MAB format\n")
        exit()

    if (not supported):
        print("This format is not yet supported\n")
        exit()

def GetMABSections(file):
    """
    Gets the list of section offsets and their respective sizes in the MAB file.
    Returns a MABOffsets file.
    """

    sections = MABOffsets()
    index = 0

    # Move the file pointer to the Section offset list
    file.seek(SECTIONOFFSETS_START, 0)

    # Get the Section sizes
    sections.UnknownSection2 = (SKIP + struct.unpack("<i", file.read(4))[0], 0)
    sections.UnknownSection1 = (SKIP + struct.unpack("<i", file.read(4))[0], 0)
    sections.Rotation =     (SKIP + struct.unpack("<i", file.read(4))[0], 0)
    sections.Keyframes =    (SKIP + struct.unpack("<i", file.read(4))[0], 0)
    sections.UnknownSection3 = (SKIP + struct.unpack("<i", file.read(4))[0], 0)
    sections.Offsets =      (SKIP + struct.unpack("<i", file.read(4))[0], 0)
    sections.Events =       (SKIP + struct.unpack("<i", file.read(4))[0], 0)
    sections.UnknownSection4 = (SKIP + struct.unpack("<i", file.read(4))[0], 0)
    sections.UnknownSection5 = (SKIP + struct.unpack("<i", file.read(4))[0], 0)

    # Get the Section sizes
    sections.UnknownSection1 = (sections.UnknownSection1[0], sections.UnknownSection2[0] - sections.UnknownSection1[0])
    sections.UnknownSection2 = (sections.UnknownSection2[0], sections.Rotation[0] - sections.UnknownSection2[0])
    sections.Rotation = (sections.Rotation[0], sections.Keyframes[0] - sections.Rotation[0])
    sections.Keyframes = (sections.Keyframes[0], sections.UnknownSection3[0] - sections.Keyframes[0])
    sections.UnknownSection3 = (sections.UnknownSection3[0], sections.Offsets[0] - sections.UnknownSection3[0])
    if (sections.Events[0] > SECTIONOFFSETS_START):
        sections.Offsets = (sections.Offsets[0], sections.Events[0] - sections.Offsets[0])
    elif (sections.UnknownSection4[0] > SECTIONOFFSETS_START):
        sections.Offsets = (sections.Offsets[0], sections.UnknownSection4[0] - sections.Offsets[0])
    else:
        sections.Offsets = (sections.Offsets[0], sections.UnknownSection5[0] - sections.Offsets[0])
    if (sections.Events[0] > SECTIONOFFSETS_START):
        if (sections.UnknownSection4[0] > SECTIONOFFSETS_START):
            sections.Events = (sections.Events[0], sections.UnknownSection4[0] - sections.Events[0])
        else:
            sections.Events = (sections.Events[0], sections.UnknownSection5[0] - sections.Events[0])
    else:
        sections.Events = (0, 0)
    if (sections.UnknownSection4[0] > SECTIONOFFSETS_START):
        sections.UnknownSection4 = (sections.UnknownSection4[0], sections.UnknownSection5[0] - sections.UnknownSection4[0])
    else:
        sections.UnknownSection4 = (0, 0)
    sections.UnknownSection5 = (sections.UnknownSection5[0], (os.fstat(file.fileno()).st_size ) - sections.UnknownSection5[0])

    return sections

def GetSkeletonBones(file):
    """
    Reads a skeleton file and returns a list of bone names 
    """

    if (struct.unpack("3s", file.read(3))[0].decode('ascii') != "LKS"):
        print("This is not a skeleton file\n")
        exit()

    # Read the bone count
    file.seek(16, 0)
    bonecount = struct.unpack("<H", file.read(2))[0]

    # Read each bone
    bones = []
    file.seek(68, 0)
    for i in range(bonecount):
        stringsize = struct.unpack("<I", file.read(4))[0]
        bones.append(struct.unpack(str(stringsize)+"s", file.read(stringsize))[0].decode('ascii'))
        file.seek(48, 1)

    return bones

def ParseSection_RotationKeyframes(file, sectionoffset, animlength_inseconds, bonecount):
    """
    Parses the RotationKeyframes section of the MAB file
    """

    file.seek(sectionoffset, 0)

    # Skip the first two WORDs
    file.seek(2 + 2, 1)

    # Read the magic float value
    magicfloat = struct.unpack("<f", file.read(4))[0]

    # Get the last offset value
    lastoffset = ((int(magicfloat*animlength_inseconds) >> 3)*4) + 8 

    # Get the section size (without padding)
    file.seek(sectionoffset+lastoffset+4, 0)
    sectionsize_nopadding = struct.unpack("<i", file.read(4))[0]

    # Now get each section
    sections = []
    curoffset = 0
    file.seek(sectionoffset+8, 0)
    while (curoffset < sectionsize_nopadding):
        kf = RotKeyFrameSection()
        kf.OffsetStart = struct.unpack("<i", file.read(4))[0]
        kf.Size = struct.unpack("<i", file.read(4))[0] - kf.OffsetStart
        file.seek(-4, 1)
        sections.append(kf)
        curoffset = kf.OffsetStart + kf.Size
    print(*sections, sep="\n")


"""=============================
       Script Entrypoint
============================="""

def main():
    """
    Program entrypoint
    """

    if (len(sys.argv) < 3):
        print("Usage:\npython3 animparser.py <animation.mab> <bones.skeleton>\n")
        exit()

    # Try to open the animation file
    try:
        fanim = open(sys.argv[1], "rb")
    except FileNotFoundError:
        print("Unable to open the animation file\n")
        exit()

    # Now lets open the skeleton file
    try:
        fskel = open(sys.argv[2], "rb")
    except FileNotFoundError:
        print("Unable to open the sekeleton file\n")
        exit()

    # Ensure it's a valid MAB file that we know how to parse
    GetMABVersion(fanim)

    # Get the file's Sections
    sections = GetMABSections(fanim)

    # Get the animation length
    fanim.seek(ANIMATIONLENGTH_START, 0)
    animlength_inseconds = struct.unpack("<f", fanim.read(4))[0]

    # Print stuff
    if (DEBUG):
        tobin = lambda x, count=16: "".join(map(lambda y:str((x>>y)&1), range(count-1, -1, -1)))
        print("Animation Length (In Seconds) - "+str(animlength_inseconds))
        print("Unknown Section 1  - "+hex(sections.UnknownSection1[0])+","+str(sections.UnknownSection1[1]))
        print("Unknown Section 2  - "+hex(sections.UnknownSection2[0])+","+str(sections.UnknownSection2[1]))
        print("Root Rotation      - "+hex(sections.Rotation[0])+","+str(sections.Rotation[1]))
        print("Rotation Keyframes - "+hex(sections.Keyframes[0])+","+str(sections.Keyframes[1]))
        print("Unknown Section 3  - "+hex(sections.UnknownSection3[0])+","+str(sections.UnknownSection3[1]))
        print("Offset Animation   - "+hex(sections.Offsets[0])+","+str(sections.Offsets[1]))
        print("Events             - "+hex(sections.Events[0])+","+str(sections.Events[1]))
        print("Unknown Section 4  - "+hex(sections.UnknownSection4[0])+","+str(sections.UnknownSection4[1]))
        print("Unknown Section 5  - "+hex(sections.UnknownSection5[0])+","+str(sections.UnknownSection5[1]))
    
    # Get the bones list
    bones = GetSkeletonBones(fskel)
    if (DEBUG):
        print("\nBones: " + str(bones)+"\n")

    # Parse the Rotation Keyframes section
    ParseSection_RotationKeyframes(fanim, sections.Keyframes[0], animlength_inseconds, len(bones))

    # Close the files as we're done with them
    fanim.close()
    fskel.close()

    print("\nFinished!\n")

main()