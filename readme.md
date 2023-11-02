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
