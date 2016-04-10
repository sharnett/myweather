1. download [miniconda](http://conda.pydata.org/miniconda.html) (to manage dependencies)
2. run `conda create --name seanweather --file conda-requirements.txt` to install the dependencies. (you might need to add `-c travis` and `-c coursera` to get some of them)
3. get an API key from [weather underground](http://www.wunderground.com/weather/api/)
4. run `export WUNDERGROUND_KEY="your_api_key"` to make it accessible to the seanweather scripts
5. run `conda activate seanweather` to load the python environment
6. launch seanweather by running `python main.py`


Check out the [live version](http://www.seanweather.com)
