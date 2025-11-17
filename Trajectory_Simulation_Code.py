
import arcpy
import os
import numpy as np
import math
from arcpy import sa

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

def flowdir_to_offset(code, cellsize):
    if code == 1: return 0, 1, cellsize
    elif code == 2: return 1, 1, math.sqrt(2) * cellsize
    elif code == 4: return 1, 0, cellsize
    elif code == 8: return 1, -1, math.sqrt(2) * cellsize
    elif code == 16: return 0, -1, cellsize
    elif code == 32: return -1, -1, math.sqrt(2) * cellsize
    elif code == 64: return -1, 0, cellsize
    elif code == 128: return -1, 1, math.sqrt(2) * cellsize
    else: return None

def ensure_folder(path):
    if path and not os.path.exists(path):
        os.makedirs(path)

def main(dem_path, flowdir_path, prone_path, out_folder,
         pixel_size=84.626292317351, slope_min=6.0, depths=[20,50,80], volume_thresh=1e6):
    arcpy.AddMessage("Reading rasters...")
    dem_r = arcpy.Raster(dem_path)
    flow_r = arcpy.Raster(flowdir_path)
    prone_r = arcpy.Raster(prone_path)
    nrows = dem_r.height
    ncols = dem_r.width
    arcpy.AddMessage(f"Raster size: {nrows} rows x {ncols} cols")

    dem_arr = arcpy.RasterToNumPyArray(dem_r, nodata_to_value=np.nan).astype(np.float32)
    flow_arr = arcpy.RasterToNumPyArray(flow_r, nodata_to_value=-9999).astype(np.int32)
    prone_arr = arcpy.RasterToNumPyArray(prone_r, nodata_to_value=0).astype(np.int32)
    prone_arr[prone_arr != 1] = 0
    pixel_area = pixel_size * pixel_size

    arcpy.AddMessage("Computing connected prone regions...")
    temp_bin = os.path.join(arcpy.env.scratchGDB, "temp_prone_bin")
    sa.Con(prone_r >= 1, 1, 0).save(temp_bin)
    rg = sa.RegionGroup(temp_bin, "EIGHT", "WITHIN", "NO_LINK")
    rg_path = os.path.join(arcpy.env.scratchGDB, "temp_prone_rg")
    rg.save(rg_path)
    rg_arr = arcpy.RasterToNumPyArray(rg_path, nodata_to_value=0).astype(np.int32)
    unique, counts = np.unique(rg_arr[rg_arr>0], return_counts=True)
    region_size_map = dict(zip(unique.tolist(), counts.tolist()))
    region_area_arr = np.zeros_like(rg_arr, dtype=np.float32)
    for k, v in region_size_map.items():
        region_area_arr[rg_arr == k] = v * pixel_area

    out_dict = {d: np.zeros((nrows, ncols), dtype=np.float32) for d in depths}

    candidate_mask = (prone_arr >= 1) & np.isfinite(dem_arr) & (flow_arr > 0)
    candidate_indices = np.transpose(np.nonzero(candidate_mask))
    arcpy.AddMessage(f"Total candidate pixels: {len(candidate_indices)}")
    max_steps = max(nrows, ncols) * 20

    for idx, (r0, c0) in enumerate(candidate_indices):
        if idx % 500 == 0:
            arcpy.AddMessage(f"Processing {idx}/{len(candidate_indices)} pixels...")
        elev0 = dem_arr[r0, c0]
        if not np.isfinite(elev0):
            continue
        src_area = region_area_arr[r0, c0] if region_area_arr[r0, c0] > 0 else pixel_area
        for depth in depths:
            volume = depth * src_area
            if volume < volume_thresh:
                continue
            alpha_deg = math.degrees(math.atan(1.4082 - 0.1658 * math.log10(volume)))
            alpha_deg = max(alpha_deg, slope_min)
            r_path, c_path = r0, c0
            path_len = 0.0
            steps = 0
            while True:
                fd_code = flow_arr[r_path, c_path]
                offset = flowdir_to_offset(fd_code, pixel_size)
                if offset is None:
                    break
                dr, dc, dist = offset
                r_next = r_path + dr
                c_next = c_path + dc
                if r_next < 0 or r_next >= nrows or c_next < 0 or c_next >= ncols:
                    break
                path_len += dist
                elev_next = dem_arr[r_next, c_next]
                if not np.isfinite(elev_next):
                    break
                slope_deg = math.degrees(math.atan((elev0 - elev_next)/path_len)) if path_len > 0 else 90
                if slope_deg > alpha_deg:
                    out_dict[depth][r_next, c_next] = depth
                    r_path, c_path = r_next, c_next
                else:
                    break
                steps += 1
                if steps > max_steps:
                    break

    arcpy.AddMessage("Saving output rasters...")
    ensure_folder(out_folder)
    lower_left = arcpy.Point(dem_r.extent.XMin, dem_r.extent.YMin)
    for depth, arr in out_dict.items():

        raster_out = arcpy.NumPyArrayToRaster(
            arr,                  
            lower_left,           
            pixel_size,           
            pixel_size,           
            value_to_nodata=0     
        )
 
        arcpy.DefineProjection_management(raster_out, dem_r.spatialReference)

        out_name = os.path.join(out_folder, f"Trajectory_{int(depth)}m.tif")
        raster_out.save(out_name)
        arcpy.AddMessage(f"Saved: {out_name}")

if __name__ == "__main__":
    dem_path = arcpy.GetParameterAsText(0)
    flowdir_path = arcpy.GetParameterAsText(1)
    prone_path = arcpy.GetParameterAsText(2)
    out_folder = arcpy.GetParameterAsText(3)
    pixel_size_txt = arcpy.GetParameterAsText(4)
    slope_min_txt = arcpy.GetParameterAsText(5)
    depths_txt = arcpy.GetParameterAsText(6)
    volume_thresh_txt = arcpy.GetParameterAsText(7)
    pixel_size = float(pixel_size_txt) if pixel_size_txt else 84.626292317351
    slope_min = float(slope_min_txt) if slope_min_txt else 6.0
    depths = [int(x) for x in depths_txt.split(",")] if depths_txt else [20,50,80]
    volume_thresh = float(volume_thresh_txt) if volume_thresh_txt else 1e6
    main(dem_path, flowdir_path, prone_path, out_folder,
         pixel_size=pixel_size, slope_min=slope_min,
         depths=depths, volume_thresh=volume_thresh)
