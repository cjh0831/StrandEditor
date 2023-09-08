import cv2
import struct
import numpy as np
import scipy.io as scio
from GenVoxelGrid import Voxel
from Hair import Hair

class VoxelHair():
    def __init__(self, gridSize = 128, dbBustObj = "DB_Bust.obj"):
        self.verts = []
        self.points = []
        self.voxel = Voxel(gridSize)
        self.voxel.genVoxel(dbBustObj)
        self.size = self.voxel.size()
        self.delta = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    self.delta.append([dx, dy, dz])
        self.delta = np.array(self.delta)

    def genDire(self):
        self.dire = np.zeros_like(self.points)
        index = 0
        for vert in self.verts:
            vertPoints = self.points[index:index+vert]
            self.dire[index:index+vert] = np.concatenate([vertPoints, vertPoints[-1, None, :]])[1:] - np.concatenate([vertPoints[0, None, :], vertPoints])[:-1]
            index += vert
        self.dire = self.dire / np.repeat(np.linalg.norm(self.dire, axis=1), 3).reshape(-1, 3)

    def loadHair(self, hair):
        assert isinstance(hair, Hair)
        self.verts = hair.getNumVerts()
        self.points = hair.getPoints()
        self.genDire()

    def genOcc(self, delta = 10):
        self.occ = np.zeros(list(self.voxel.size()))

        index = 0

        deltaV = 1 / delta * (np.array(range(delta-1)) + 1)
        for vert in self.verts:
            points = self.points[index:index+vert]
            dec = (points[1:] - points[:-1]).reshape(-1)
            delta_points = np.repeat(points[np.newaxis, :-1, :], delta-1, axis=0) + np.matmul(deltaV[:, np.newaxis], dec[np.newaxis, :]).reshape(9, -1, 3)
            delta_points = np.concatenate([delta_points.reshape(-1, 3), points])
            voxel_result, _ = self.voxel.getGIndiceForPos(delta_points)
            self.occ[voxel_result[:, 0], voxel_result[:, 1], voxel_result[:, 2]] = 1
            index += vert

    def genOri(self):

        import time
        start = time.time()

        size = list(self.voxel.size())
        poolSize = np.zeros(size)
        fieldOriVari = np.zeros(size)
        voxelConf = np.zeros(size)

        size.append(3)
        self.ori = np.zeros(size)
        oriMean = np.zeros(size)

        voxel_result, delete_id = self.voxel.getGIndiceForPos(self.points)
        delete_dire = np.delete(self.dire, delete_id, axis=0)

        np.add.at(oriMean, (voxel_result[:, 0], voxel_result[:, 1], voxel_result[:, 2]), delete_dire)
        np.add.at(poolSize, (voxel_result[:, 0], voxel_result[:, 1], voxel_result[:, 2]), 1)
        # for i in range(voxel_result.shape[0]):
        #     oriMean[voxel_result[i, 0], voxel_result[i, 1], voxel_result[i, 2], :] += delete_dire[i, :]
        #     poolSize[voxel_result[i, 0], voxel_result[i, 1], voxel_result[i, 2]] += 1

        oriMean = oriMean / np.clip(np.repeat(poolSize[..., np.newaxis], 3, axis=-1), 1., np.inf)
        has_size = np.where(poolSize > 0)
        oriMean[has_size] = oriMean[has_size] / np.repeat(np.linalg.norm(oriMean[has_size], axis=-1)[..., np.newaxis], 3, axis=-1)

        var = (np.sum(delete_dire[:, ...] * oriMean[voxel_result[:, 0], voxel_result[:, 1], voxel_result[:, 2], ...], axis=1) - 1.)**2
        np.add.at(fieldOriVari, (voxel_result[:, 0], voxel_result[:, 1], voxel_result[:, 2]), var)
        # for i in range(delete_dire.shape[0]):
        #     fieldOriVari[voxel_result[i, 0], voxel_result[i, 1], voxel_result[i, 2]] += var[i]
        
        fieldOriVari = np.clip(100. * fieldOriVari / np.clip(poolSize, 1., np.inf), 1e-7, np.inf)

        self.ori = oriMean.copy()
        conf = 10. * np.exp(-var[:] / (2. * fieldOriVari[voxel_result[:, 0], voxel_result[:, 1], voxel_result[:, 2]]))
        for i in range(delete_dire.shape[0]):
            if (conf[i] > voxelConf[voxel_result[i, 0], voxel_result[i, 1], voxel_result[i, 2]]):
                voxelConf[voxel_result[i, 0], voxel_result[i, 1], voxel_result[i, 2]] = conf[i]
                self.ori[voxel_result[i, 0], voxel_result[i, 1], voxel_result[i, 2]] = delete_dire[i]

        hasOcc = np.where(self.occ > 0)
        noOri = np.where(np.sum(self.ori[hasOcc]**2, axis=1) == 0)[0]
        while (len(noOri) > 0):
            for i in noOri:
                x, y, z = hasOcc[0][i], hasOcc[1][i], hasOcc[2][i]
                delta = self.delta + [x, y, z]
                dx = np.clip(delta[:, 0], 0, self.size[0]-1)
                dy = np.clip(delta[:, 1], 0, self.size[1]-1)
                dz = np.clip(delta[:, 2], 0, self.size[2]-1)

                newOri = np.sum(self.ori[dx, dy, dz], axis=0) / 9
                self.ori[x, y, z] = newOri / np.linalg.norm(newOri)

            noOri = np.where(np.sum(self.ori[hasOcc]**2, axis=1) == 0)[0]

    def saveOcc(self, occMat = "Occ3D.mat"):
        result = {}
        result["Occ"] = np.flip(self.occ, axis=[1, 2]).transpose(1, 0, 2)
        scio.savemat(occMat, result)

    def saveOri(self, oriMat = "Ori_gt.mat"):
        result = {}
        result["Ori"] = np.flip(self.ori, axis=[1, 2]).transpose(1, 0, 3, 2).reshape(self.size[0], self.size[1], self.size[2] * 3)
        scio.savemat(oriMat, result)

    def saveMask(self, maskFile = "mask.png"):
        mask = np.clip(np.sum(self.occ, axis=-1), 0, 1)
        cv2.imwrite(maskFile, mask * 255)

if __name__ == "__main__":
    import time
    start = time.time()
    hair = Hair()
    hairVoxel = VoxelHair(gridSize = 512)
    end = time.time()
    print("inti: ", end - start)
    start = end

    hair.loadAbcHair("/mnt/e/YDNB/NeuralHDHair/mh2usc_hair/test/Male_Hair_016_usc.abc")
    hairVoxel.loadHair(hair)
    hairVoxel.genOcc()
    hairVoxel.genOri()
    hairVoxel.saveOcc("/mnt/e/YDNB/NeuralHDHair/mh2usc_hair/test/Occ3D_pred.mat")
    hairVoxel.saveOri("/mnt/e/YDNB/NeuralHDHair/mh2usc_hair/test/Ori3D_pred.mat")

    # hair.loadHairHair("/mnt/e/YDNB/NeuralHDHair/mh2usc_hair/test/Male_Hair_016_usc.hair")
    # hairVoxel.loadHair(hair)
    # hairVoxel.genOcc()
    # hairVoxel.genOri()
    # hairVoxel.saveOcc("/mnt/e/YDNB/NeuralHDHair/mh2usc_hair/test/Occ3D.mat")
    # hairVoxel.saveOri("/mnt/e/YDNB/NeuralHDHair/mh2usc_hair/test/Ori3D.mat")

