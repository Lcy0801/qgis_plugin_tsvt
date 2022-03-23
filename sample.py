from osgeo import gdal, gdalconst, osr
import struct
import numpy as np
import os


def geo2pixel(geot: list, geo: list):
    px = (geot[5] * geo[0] - geot[2] * geo[1] - geot[0] * geot[5] + geot[2] * geot[3]) / (
            geot[1] * geot[5] - geot[2] * geot[4])
    py = (geot[4] * geo[0] - geot[1] * geo[1] + geot[1] * geot[3] - geot[4] * geot[0]) / (
            geot[2] * geot[4] - geot[1] * geot[5])
    return px, py


def sample(fileName, bandindex, px, py):
    if not (os.path.exists(fileName)):
        return np.nan
    gdal.AllRegister()
    ds = gdal.Open(fileName, gdalconst.GA_ReadOnly)
    if ds == None:
        return np.nan
    bandcount = ds.RasterCount
    if bandindex > bandcount:
        return np.nan
    xSize = ds.RasterXSize
    ySize = ds.RasterYSize
    if px > (xSize - 1) or px < 0 or py > (ySize - 1) or py<0:
        return np.nan
    band = gdal.Dataset.GetRasterBand(ds, bandindex)
    values = gdal.Band.ReadRaster(band, int(px), int(py), 1, 1, 1, 1, gdalconst.GDT_Float32)
    values = struct.unpack('f' * 1, values)
    ds = None
    band = None
    return values[0]


def coordTransform(srsSource, srsDest, x, y):
    coordTransformation = osr.CreateCoordinateTransformation(srsSource, srsDest)
    if osr.SpatialReference.IsProjected(srsSource):
        dstX, dstY, _ = (coordTransformation.TransformPoint(x, y))
    else:
        dstX, dstY, _ = (coordTransformation.TransformPoint(y, x))
    if osr.SpatialReference.IsProjected(srsDest):
        return dstX, dstY
    else:
        return dstY, dstX


if __name__ == "__main__":
    srs3857 = osr.SpatialReference()
    srs3857.ImportFromEPSG(3857)
    srs4326 = osr.SpatialReference()
    srs4326.ImportFromEPSG(4326)
    x, y = coordTransform(srs3857, srs4326, -13512193.353434978, 12374598.345831176)
    print(x, y)
