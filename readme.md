### its_live web portal tutorial
The main purpose of this tutorial is to show how to use NASA's
[its_live web portal](https://nsidc.org/apps/itslive/) to download image pair velocities. 

Many other tutorials exist that are great. For example Emma Marshal's [Using xarray to examine cloud-based glacier surface velocity data](https://e-marshall.github.io/itslive/intro.html). Her tools utilizes its_live's data cubes so you can use the image pair velocity products without having to download them. In the future, I plan to  make a tutorial using Emma's  [itslivetools](https://github.com/e-marshall/itslivetools) for Greenland specific data.

## installation
Below are instructions for installation with a UNIX terminal.

To use this repo first clone the repository and change to the directory where the repo is located
```
git clone https://github.com/shahinmg/its_live_tutorial.git

cd its_live_tutorial
```

Within the `its_live_tutorial` directory, install the packages in the `environment.yml` in a conda environment or create a new environment and install with `conda env create --file environment.yml` and activate the environment  

Note: This can take a long time to create the environment

```
conda env create --file environment.yml

conda activate its_live_tutorial
```

In the `its_live_tutorial` directory run

```
jupyter lab
```
and open the `its_live_web_app_tutorial.ipynb` notebook

### its_live  API_tutorial

Similar to the first tutorial, the `ITS_LIVE API_tutorial.ipynb` shows how to fetch its_live image pair velocities from their s3 bucket and use the data without having to download it. Also, in this tutorial we calculate strain rates from [`iceutils`](https://github.com/bryanvriel/iceutils). Similar to the [`measures_strain_rates`](https://github.com/shahinmg/measures_strain_rates) repo. 

### its_live_datacube_tutorial.ipynb & its_live_datacube_term_poly_tutorial

These tutorials use the ITS_LIVE datacube instead of the API
`its_live_datacube_tutorial.ipynb` plots a velocity time series at Helehim Glacier. 
`its_live_datacube_term_poly_tutorial` clips a terminus polygon at sermeq kujalleq and calculates average terminus velocity.

## Installation

If you installed the packages in the `environment.yml` from the first tutorial, you are good to go. if not follow the same instructions as the `its_live web portal tutorial`.

To install `iceutils`, you may clone a read-only version of the repository:

```
git clone https://github.com/bryanvriel/iceutils.git
```
Or, if you are developer, you may clone with SSH:

```
git clone git@github.com:bryanvriel/iceutils.git
```
Then, simply run `pip install .` in the main repository directory to install.

In the cloned directory, you'll find several Python source files, each containing various functions and classes. While the naming of the source files gives a hint about what they contain, all functions are classes are imported into a common namespace. For example, the file `stress.py` contains a function `compute_stress_strain()`. This function would be called as follows:

```python
import iceutils as ice

stress_strain = ice.compute_stress_strain(vx, vy)
```
