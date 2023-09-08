import os
import struct
import numpy as np
try:
    from imath import *
    from alembic.Abc import *
    from alembic.AbcGeom import *
    from alembic.AbcCoreAbstract import *
except ImportError:
    print("Has no alembic sdk")

class Hair():
    def __init__(self):
        self.nVerts = []
        self.points = []

    def loadHairHair(self, hairFile):
        self.nVerts = []
        self.points = []
        with open(hairFile, "rb") as file:
            file.read(4)
            hair_count = struct.unpack('i', file.read(4))[0]
            point_count = struct.unpack('i', file.read(4))[0]
            arrays = struct.unpack('i', file.read(4))[0]
            d_segments = struct.unpack('i', file.read(4))[0]
            d_thickness = struct.unpack('f', file.read(4))[0]
            d_transparency = struct.unpack('f', file.read(4))[0]
            d_color = struct.unpack('fff', file.read(4 * 3))
            file.read(88)

            segments = struct.unpack('h' * hair_count, file.read(2 * hair_count))
            self.nVerts = np.array(segments) + 1
            
            points = struct.unpack('f' * point_count * 3, file.read(4 * point_count * 3))
            self.points = np.array(points).reshape(-1, 3)

    def toHairHair(self, outputFile):
        assert type(self.points) is np.ndarray and type(self.nVerts) is np.ndarray
        assert np.sum(self.nVerts) == self.points.shape[0]

        with open(outputFile, "wb") as file:
            file.write(b"hair")
            file.write(struct.pack("i", self.nVerts.shape[0]))
            file.write(struct.pack("i", self.points.shape[0]))
            file.write(struct.pack("i", 0))
            file.write(struct.pack("i", 0))
            file.write(struct.pack("f", 0.))
            file.write(struct.pack("f", 0.))
            file.write(struct.pack("fff", 0., 0., 0.))
            for i in range(88):
                file.write(b"\0")
            
            for vert in self.nVerts:
                file.write(struct.pack("h", vert-1))

            for point in self.points:
                file.write(struct.pack("fff", *point))
    
    def hasAlembic(self):
        try:
            oxform = OXform()
            return True
        except Exception:
            print("Has no alembic sdk")
            return False

    def loadAbcHair(self, abcFile):
        if not self.hasAlembic():
            return

        self.nVerts = []
        self.points = []
        def readArrayProp(iprop, name, map):
            numSamples = iprop.getNumSamples()

            for i in range(numSamples):
                samp = iprop.getValue(ISampleSelector(i))
                if iprop.getName() == "P" or iprop.getName() == "nVertices":    # 
                    samp = np.asarray(samp)
                    map[name][iprop.getName()] = samp

        def readScalarProp(iprop):
            pass

        def readCompoundProp(iprop, name, map):
            childNum = iprop.getNumProperties()
            if not name in map:
                map[name] = {}
            for i in range(childNum):
                header = iprop.getPropertyHeader(i)
                if header.isArray():
                    readArrayProp(IArrayProperty(iprop, header.getName()), name, map)
                if header.isScalar():
                    readScalarProp(IScalarProperty(iprop, header.getName()))
                if header.isCompound():
                    readCompoundProp(ICompoundProperty(iprop, header.getName()), name, map)

        def readObject(iobj, map):
            iprop = iobj.getProperties()
            readCompoundProp(iprop, iobj.getFullName(), map)
            for i in range(iobj.getNumChildren()):
                icobj = iobj.getChild(i)
                readObject(icobj, map)

        itopObj = IArchive(abcFile).getTop()
        map = {}
        readObject(itopObj, map)

        for name in map:
            if "P" not in map[name]:
                continue

            points = map[name]["P"]
            verts = map[name]["nVertices"]

            self.points.extend(points)
            self.nVerts.extend(verts)

        self.points = np.array(self.points)
        self.nVerts = np.array(self.nVerts)

    def toAbcHair(self, outputFile):
        if not self.hasAlembic():
            return
        assert type(self.points) is np.ndarray and type(self.nVerts) is np.ndarray
        assert np.sum(self.nVerts) == self.points.shape[0]

        def setArray(iTPTraits, iList):
            array = iTPTraits.arrayType(len(iList))
            for i in range(len(iList)):
                array[i] = iList[i]
            return array

        oxform = OXform(OArchive(outputFile).getTop(), "hairOxForm")
        ocurveObj = OCurves(oxform, "hair")
        ocurve = ocurveObj.getSchema()

        kCubic = CurveType.kCubic
        kNonPeriodic = CurvePeriodicity.kNonPeriodic

        pos = []
        for point in self.points:
            pos.append(V3f((point[0], point[1], point[2]))),

        pos = setArray(V3fTPTraits, pos)
        verts = setArray(Int32TPTraits, self.nVerts.tolist())

        ocurveSamp = OCurvesSchemaSample(pos, verts, kCubic, kNonPeriodic)
        ocurve.set(ocurveSamp)

    def getPoints(self):
        return self.points
    def getNumVerts(self):
        return self.nVerts
    
    def setPoints(self, points):
        points = np.array(points)
        assert len(points.shape) == 2
        assert points.shape[1] == 3
        self.points = np.array(points)
    def setNumVerts(self, nVerts):
        nVerts = np.array(nVerts).astype(np.int32)
        assert len(nVerts.shape) == 1
        self.nVerts = nVerts


if __name__ == "__main__":
    import os
    import random
    input_dir = "/mnt/e/YDNB/NeuralHDHair/mh2usc_hair/mh2usc_hair_big"
    output_dir = "/mnt/e/YDNB/NeuralHDHair/mh2usc_hair/mh2usc_abc_big"
    os.makedirs(output_dir, exist_ok=True)
    hair = Hair()
    for file in os.listdir(input_dir):
        hair.loadHairHair(os.path.join(input_dir, file))
        nVerts = hair.getNumVerts()
        points = hair.getPoints()

        index = 0
        randVerts = np.random.rand(nVerts.shape[0])

        threshold = 60000 / nVerts.shape[0]
        print(threshold)
        newNVerts = nVerts[randVerts < threshold]
        deleteIndex = []
        for i, vert in enumerate(nVerts):
            if randVerts[i] >= threshold:
                deleteIndex.append(np.arange(vert) + index)
            index += vert
        if deleteIndex != []:
            deleteIndex = np.concatenate(deleteIndex)
            print(deleteIndex.shape)
            print(points.shape)
            points = np.delete(points, deleteIndex, axis=0)
        print(points.shape)
        hair.setNumVerts(newNVerts)
        hair.setPoints(points)
        hair.toAbcHair(os.path.join(output_dir, "{}.abc".format(file.split(".")[0])))