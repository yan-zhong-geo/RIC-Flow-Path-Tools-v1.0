# RIC Flow Path Tools v1.0

**Developer:** [Yan Zhong](https://sites.google.com/view/yanzhong-geo), [University of Geneva](https://c-cia.ch/)  
**E-mails:** yan.zhong@unige.ch | yan.zhong.geo@gmail.com  
**Toolbox file:** `RIC Flow Path Tools v1.0.atbx`  
**Version:** 1.0  
**Last updated:** 12.09.2025  
**Language:** English  
**Coding language:** Python  
**Operating System:** Windows (ArcGIS 10.0 or later, including ArcGIS Pro)  
**Installation Time:** ~1 second  

---

## 1. Overview
**RIC Flow Path Tools v1.0** is an ArcGIS toolbox for automated simulation and assessment of potential mass movement trajectories in high mountain regions, focusing on **rock-ice collapses** and their interactions with **hydropower installations**.

It integrates terrain preprocessing, detachment zone identification, and trajectory simulation into one workflow. The toolbox supports **batch processing**, **exposure filtering**, and **regional hazard screening**.

This toolbox accompanies the paper:  
> Zhong, Y., Allen, S., … Stoffel, M. (2026). *Cascading Rock-Ice Collapses Threaten Hydropower in High Mountain Asia*  

Please cite this publication when using the toolbox.

<figure>
  <img src="https://github.com/user-attachments/assets/2a73f65f-dbd4-4236-b922-54ca8ca1e68e" alt="Simulated mass-flow paths" width="600"/><br>
  <figcaption>Figure: Simulated mass-flow paths reaching downstream hydropower installations under three detachment-zone depth scenarios, shown as an example application.</figcaption>
</figure>

---

## 2. Toolbox Structure

| # | Tool Name | Function Summary |
|---|------------|------------------|
| 1 | DEMfill & FlowDir | Prepares DEM and computes D8 flow direction. |
| 2 | Potential Detachment Zones | Identifies possible detachment areas based on terrain and cryospheric thresholds. |
| 3 | Trajectory Simulation v2.0 | Simulates all trajectories from source areas. |
| 4 | Trajectory Simulation v2.1 Exposure Index | Simulates trajectories and computes weighted exposure indices. |
| 5 | Trajectory Simulation v2.2 Exposure Only | Exposure-filtered trajectory simulation. |

---

## 3. Tool Descriptions

### 3.1 DEMfill & FlowDir

| **Inputs** | **Data Type** | **Description** |
|-------------|---------------|-----------------|
| DEM | Raster | Digital Elevation Model |

| **Outputs** | **Data Type** | **Description** |
|--------------|---------------|-----------------|
| Filled DEM | Raster | Hydrologically corrected DEM |
| Flow Direction | Raster | D8 flow direction raster |

---

### 3.2 Potential Detachment Zones

| **Inputs** | **Data Type** | **Description** |
|-------------|---------------|-----------------|
| Filled DEM | Raster | Hydrologically filled DEM |
| Permafrost Index Zones | Raster | Raster map of permafrost probability |
| Glacier Boundaries | Polygon | Glacier outlines for exclusion or masking |

| **Outputs** | **Data Type** | **Description** |
|--------------|---------------|-----------------|
| Potential Detachment Zones | Raster | Source-prone zones satisfying terrain and cryospheric thresholds |

---

### 3.3–3.5 Trajectory Simulation v2.0–v2.2

| **Inputs** | **Data Type** | **Description** |
|-------------|---------------|-----------------|
| Filled DEM | Raster | Digital Elevation Model |
| Flow Direction | Raster | D8 flow direction raster |
| Prone Area | Raster | Binary raster of potential detachment zones |
| Exposure Raster *(v2.1 only)* | Raster | Binary exposure raster |
| Output Folder | Folder | Directory to save simulation results |
| Pixel Size *(optional)* | Float | Cell size (default = 84.6263 m) |
| Minimum Slope *(optional)* | Float | Lower bound of α (default = 6°) |
| Depths *(optional)* | String | Simulated flow thicknesses (default = 20, 50, 80 m) |
| Volume Threshold *(optional)* | Float | Minimum source volume (default = 1e6 m³) |

| **Outputs** | **Data Type** | **Description** |
|--------------|---------------|-----------------|
| Trajectory_20m.tif | Raster | Flow path extent for 20 m thickness |
| Trajectory_50m.tif | Raster | Flow path extent for 50 m thickness |
| Trajectory_80m.tif | Raster | Flow path extent for 80 m thickness |

> **Note:** Demo data are provided in the tools package for model demonstration and validation purposes.  
> **Expected run time:** ~40 seconds on a standard desktop computer.

---

## 4. Workflow Example
1. **Prepare DEM & Flow Direction** → Run *DEMfill & FlowDir*.  
2. **Identify Detachment Zones** → Run *Potential Detachment Zones*.  
3. **Simulate Trajectories** → Use *Trajectory Simulation v2.0 / v2.1 / v2.2*.  
4. **Analyze Exposure** → Overlay `Trajectory_*m.tif` with infrastructure maps.  
5. **Summarize Risk** → Use `Other_code.ipynb` in Jupyter/Colab for post-processing.

---

## 5. Tips Before Running
1. Fill the DEM before computing flow direction.  
2. Resample all rasters to the same **cell size**, **extent (columns and rows)**, and **projection**.  
3. Ensure consistent **projection** and **meter units**.  
4. Use **32-bit float rasters** for compatibility with ArcPy and NumPy.

---

## License
See the [LICENSE](LICENSE) file for full terms.
