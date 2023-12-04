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

class MeshBone:
    """
    Stores the bone's name and its parent's
    """
    Name: str
    Parent: str

    def __init__(self):
        self.Name = ""
        self.Parent = ""

    def __repr__(self) -> str:
        if (self.Parent == ""):
            return f"{type(self).__name__}(Name=\"{self.Name}\")"
        else:
            return f"{type(self).__name__}(Name=\"{self.Name}\", Parent=\"{self.Parent}\")"

class RotKeyFrameSection:
    """
    Stores helper information about the rotation keyframe section
    """

    OffsetStart: int
    Size: int

    def __repr__(self) -> str:
        return f"{type(self).__name__}(start={hex(self.OffsetStart)}, size={self.Size})"

class Quaternion:
    x: float
    y: float
    z: float
    w: float

    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __repr__(self) -> str:
        return f"{type(self).__name__}(x={'{0:.10f}'.format(self.x)}, y={'{0:.10f}'.format(self.y)}, z={'{0:.10f}'.format(self.z)}, w={'{0:.10f}'.format(self.w)})"

    def euler(self) -> str:
        pitch = math.asin(-2.0*(self.x*self.z - self.w*self.y));
        yaw = math.atan2(2.0*(self.y*self.z + self.w*self.x), self.w*self.w - self.x*self.x - self.y*self.y + self.z*self.z);
        roll = math.atan2(2.0*(self.x*self.y + self.w*self.z), self.w*self.w + self.x*self.x - self.y*self.y - self.z*self.z);
        return (math.degrees(pitch), math.degrees(yaw), math.degrees(roll))


"""=============================
     Useful Math Functions
============================="""

def UnpackQuaternion(FirstWord, SecondWord, ThirdWord):
    fVar1 = float(FirstWord & 0x7fff) * 4.315969e-05 - 0.7071068
    fVar2 = float(SecondWord & 0x7fff) * 4.315969e-05 - 0.7071068
    fVar3 = float(ThirdWord) * 4.315969e-05 - 0.7071068
    sqrtval = 1.0 - math.pow(fVar1, 2) - math.pow(fVar2, 2) - math.pow(fVar3, 2)
    if (sqrtval < 0):
        return None
    fVar4 = math.sqrt(sqrtval)
    if ((FirstWord & 0x8000) == 0):
        if ((SecondWord & 0x8000) != 0):
            return Quaternion(fVar1, fVar2, fVar4, fVar3)
    elif ((SecondWord & 0x8000) != 0):
        return Quaternion(fVar1, fVar2, fVar3, fVar4)

    if ((FirstWord & 0x8000) != 0):
        return Quaternion(fVar1, fVar4, fVar2, fVar3)
    return Quaternion(fVar4, fVar1, fVar2, fVar3)


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
    global_mabversion = data

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

def GetMeshBones(file):
    """
    Reads a xbg mesh file and returns a list of bone names 
    """
    bones = []
    if (struct.unpack("4s", file.read(4))[0][::-1].decode('ascii') != "MESH"):
        print("This is not a mesh file\n")
        exit()
    majorver = struct.unpack("<H",file.read(2))[0]
    minorver = struct.unpack("<H",file.read(2))[0]

    file.seek(28, 0)

    # Read the chunk count
    chunkcount = struct.unpack("<L",file.read(4))[0]
    
    # Find the skeleton chunk
    for c in range(chunkcount):
        chunkstart = file.tell()
        chunkname = struct.unpack("4s",file.read(4))[0][::-1].decode("ascii")
        file.seek(4, 1)
        chunksize = struct.unpack("<L",file.read(4))[0]
        file.seek(8, 1)
        if (chunkname != "NODE"):
            file.seek(chunksize - 20, 1)
            continue

        # Iterate through all bones
        bonecount = struct.unpack("<L",file.read(4))[0]
        for i in range(bonecount):
            file.seek(12, 1)

            # Get the parent bone id
            parentid = struct.unpack("<l",file.read(4))[0]

            # Skip a bunch of bytes we don't need
            if majorver == 46:
                file.seek(48, 1)
            else:
                file.seek(40, 1)
            file.seek(12, 1)

            # Get the bone name
            namelen = struct.unpack("<L",file.read(4))[0]
            bonename = struct.unpack("%ss" %namelen, file.read(namelen))[0].decode("ascii")

            # Store it
            b = MeshBone()
            b.Name = bonename
            if (parentid >= 0 and bones[parentid] != None):
                b.Parent = bones[parentid].Name
            bones.append(b)

            # Skip more bytes so we can check the next bone
            file.seek(1,1)
            if majorver == 46:
                file.seek(4,1)
        break
    return bones

def ParseSection_RootRotations(file, sectionoffset, animlength_inseconds, bonecount):
    rots = []
    file.seek(sectionoffset, 0)
    rotcount = struct.unpack("<i", file.read(4))[0]
    file.seek(4, 1)
    for r in range(rotcount):
        FirstWord = struct.unpack("<H", file.read(2))[0]
        SecondWord = struct.unpack("<H", file.read(2))[0]
        ThirdWord = struct.unpack("<h", file.read(2))[0]
        quat = UnpackQuaternion(FirstWord, SecondWord, ThirdWord)
        rots.append(quat)
    return rots

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
    file.seek(sectionoffset + lastoffset + 4, 0)
    sectionsize_nopadding = struct.unpack("<i", file.read(4))[0]

    # Now get each subsection
    subsections = []
    curoffset = 0
    file.seek(sectionoffset + 8, 0)
    while (curoffset < sectionsize_nopadding):
        kf = RotKeyFrameSection()
        kf.OffsetStart = struct.unpack("<i", file.read(4))[0]
        kf.Size = struct.unpack("<i", file.read(4))[0] - kf.OffsetStart
        file.seek(-4, 1)
        subsections.append(kf)
        curoffset = kf.OffsetStart + kf.Size

    # Show the sections
    print("\nQuaternion Keyframe Section: ")
    for s in subsections:
        print("    " + str(s))

    # Unpack the Quaternion data
    file.seek(sectionoffset, 0)
    frame = 0
    for kf in subsections:
        print("    Frame " + str(frame))
        file.seek(sectionoffset + kf.OffsetStart, 0)

        # Read the first quaternion
        FirstWord = struct.unpack("<H", file.read(2))[0]
        SecondWord = struct.unpack("<H", file.read(2))[0]
        ThirdWord = struct.unpack("<h", file.read(2))[0]
        quat = UnpackQuaternion(FirstWord, SecondWord, ThirdWord)
        if not (quat == None):
            print("        " + str(quat.euler()))
        else:
            print("        Bad quat at " + hex(file.tell() - sectionoffset - 6))

        # Read the mystery short and count the number of 1's, which corresponds to the number of quaternions stored afterwards
        MysteryShort = struct.unpack("<B", file.read(2))[0]
        QuatCount = MysteryShort.bit_count()
        print("        " + str(QuatCount) + " quats stored afterwards")

        # Unpack all subsequent quaternions
        while (QuatCount > 0):
            FirstWord = struct.unpack("<H", file.read(2))[0]
            SecondWord = struct.unpack("<H", file.read(2))[0]
            ThirdWord = struct.unpack("<h", file.read(2))[0]
            quat = UnpackQuaternion(FirstWord, SecondWord, ThirdWord)
            if not (quat == None):
                print("        " + str(quat.euler()))
            else:
                print("        Bad quat at " + hex(file.tell() - sectionoffset - 6))
            QuatCount -= 1
        frame += 1

def TestQuaternion(str):
    data = bytearray.fromhex(str)
    FirstWord  = struct.unpack('<H', data[0:2])[0]
    print(FirstWord)
    SecondWord = struct.unpack('<H', data[2:4])[0]
    print(SecondWord)
    ThirdWord  = struct.unpack('<H', data[4:6])[0]
    print(ThirdWord)
    quat = UnpackQuaternion(FirstWord, SecondWord, ThirdWord)
    if not (quat == None):
        print(quat.euler())
    else:
        print("Bad quaternion")


"""=============================
       Script Entrypoint
============================="""

def main():
    """
    Program entrypoint
    """

    if (len(sys.argv) == 2):
        TestQuaternion(sys.argv[1])
        exit()
    if (not len(sys.argv) == 3):
        print("Usage:\npython3 animparser.py <animation.mab> <model.xbg>\n")
        exit()

    # Try to open the animation file
    try:
        fanim = open(sys.argv[1], "rb")
    except FileNotFoundError:
        print("Unable to open the animation file\n")
        exit()

    # Now lets open the skeleton file
    try:
        fmesh = open(sys.argv[2], "rb")
    except FileNotFoundError:
        print("Unable to open the mesh file\n")
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
        print("    Animation Length (In Seconds) - "+str(animlength_inseconds))
        print("    Unknown Section 1  - "+hex(sections.UnknownSection1[0])+","+str(sections.UnknownSection1[1]))
        print("    Unknown Section 2  - "+hex(sections.UnknownSection2[0])+","+str(sections.UnknownSection2[1]))
        print("    Root Rotation      - "+hex(sections.Rotation[0])+","+str(sections.Rotation[1]))
        print("    Rotation Keyframes - "+hex(sections.Keyframes[0])+","+str(sections.Keyframes[1]))
        print("    Unknown Section 3  - "+hex(sections.UnknownSection3[0])+","+str(sections.UnknownSection3[1]))
        print("    Offset Animation   - "+hex(sections.Offsets[0])+","+str(sections.Offsets[1]))
        print("    Events             - "+hex(sections.Events[0])+","+str(sections.Events[1]))
        print("    Unknown Section 4  - "+hex(sections.UnknownSection4[0])+","+str(sections.UnknownSection4[1]))
        print("    Unknown Section 5  - "+hex(sections.UnknownSection5[0])+","+str(sections.UnknownSection5[1]))
    
    # Get the bones list
    bones = GetMeshBones(fmesh)
    if (DEBUG):
        print("\nBones:")
        print("    " + str(len(bones)) + " bones")
        for b in bones:
            print("    " + str(b))

    # Parse the Root Rotation section
    rootrots = ParseSection_RootRotations(fanim, sections.Rotation[0], animlength_inseconds, len(bones))
    if (DEBUG):
        print("\nRoot Rotation Section:")
        print("    " + str(len(rootrots)) + " rotation values")
        for q in rootrots:
            print("    " + str(q.euler()))

    # Parse the Rotation Keyframes section
    ParseSection_RotationKeyframes(fanim, sections.Keyframes[0], animlength_inseconds, len(bones))

    # Close the files as we're done with them
    fanim.close()
    fmesh.close()

    print("\nFinished!\n")

main()