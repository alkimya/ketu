# Ketu

Little library to compute positions of astronomical bodies (Sun, Moon, planets
and mean Node aka Rahu), generate time series and calendars based on planetary
aspects.

Need python 3.9+, pyswisseph: `pip install pyswisseph` and numpy: `pip install
numpy`

At the moment, compute bodies positions and aspects for a date.

Move to ketu directory, run `python ketu.py` to compute bodies positions and 
aspects interactively.

![Terminal screen](res/ketu.png)

## TODO

+ Find datetimes for beginning, end and exact aspect
  
+ Find all aspects between two dates

+ Refactor the API to fix bugs and make it clearer
