import numpy as np

class Voxel():
    def __init__(self, gridSize = 128):
        self.param_enlargeScale = 1.3
        self.param_XGridSize = gridSize
        self.param_GridRatio = np.array([1., 1., 0.75])
        self.m_gridSize = self.param_GridRatio * self.param_XGridSize
        self.oriOffSet = np.array([0., 0., 0.])

    def genVoxel(self, hair_obj):
        def readObj(hari_obj):
            bbox = [np.inf, -np.inf, np.inf, -np.inf, np.inf, -np.inf]
            with open(hair_obj, "r") as file:
                lines = file.readlines()
                for line in lines:
                    if not line.startswith("v "):
                        continue
                    
                    while line.find("  ") != -1:
                        line.replace("  ", " ")
                    line.replace("\n", "")
                    line.replace("\r", "")

                    strs = line.split(" ")
                    x, y, z = float(strs[1]), float(strs[2]), float(strs[3])
                    if x < bbox[0]:
                        bbox[0] = x
                    if x > bbox[1]:
                        bbox[1] = x
                    if y < bbox[2]:
                        bbox[2] = y
                    if y > bbox[3]:
                        bbox[3] = y
                    if z < bbox[4]:
                        bbox[4] = z
                    if z > bbox[5]:
                        bbox[5] = z

            return bbox
    
        bbox = readObj(hair_obj)
        modelXLen = (bbox[1] - bbox[0]) * self.param_enlargeScale
        modelYLen = modelXLen * self.param_GridRatio[1]
        self.oriOffSet[0] = (modelXLen - (bbox[1] - bbox[0])) * 0.5
        self.oriOffSet[1] = (modelYLen - (bbox[3] - bbox[2])) * 0.7
        self.oriOffSet[2] = self.param_enlargeScale * self.oriOffSet[0]
        self.m_gridOrigin = [bbox[0], bbox[2], bbox[4]]- self.oriOffSet
        self.m_gridStep = modelXLen / self.m_gridSize[0]
        self.m_gridStepInv = 1. / self.m_gridStep

    def getGIndiceForPos(self, pos):
        gridPos = (pos - self.m_gridOrigin) * self.m_gridStepInv
        gridCoord = np.floor(gridPos + 0.5)

        delete = np.concatenate([np.where(gridCoord[..., 0] < 0)[0],
                                 np.where(gridCoord[..., 1] < 0)[0],
                                 np.where(gridCoord[..., 2] < 0)[0],
                                 np.where(gridCoord[..., 0] >= self.m_gridSize[0])[0],
                                 np.where(gridCoord[..., 1] >= self.m_gridSize[1])[0],
                                 np.where(gridCoord[..., 2] >= self.m_gridSize[2])[0]])

        gridCoord = np.delete(gridCoord, delete, axis=0)

        return gridCoord.astype(np.int32), delete

    def size(self):
        return self.m_gridSize.astype(np.int32)
if __name__ == "__main__":
    voxel = Voxel(256)
    voxel.genVoxel("DB_Bust.obj")
    print(voxel.getGIndiceForPos([0, 1.6, 0]))
