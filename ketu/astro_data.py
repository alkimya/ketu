import numpy as np
import swisseph as swe


# Vectorized lambda function to decode elements of an array or list using UTF-8
utf_8 = np.vectorize(lambda x: x.decode("UTF-8"))

# Path to swisseph ephemerids
swe.set_ephe_path("ephe")

# Structured array of astronomical bodies: Sun, Moon, Mercury, Venus, Mars,
# Jupiter, Saturn, Uranus, Neptune, Pluto, mean Node aka Rahu, mean Apogee aka
# Lilith, their Swiss Ephemeris id's, their orb of influence
# (Inspired by Abu Ma’shar (787-886) and Al-Biruni (973-1050))
# and their average speed in degrees per day
bodies = np.array(
    [
        ("Sun", 0, 12, 0.986),
        ("Moon", 1, 12, 13.176),
        ("Mercury", 2, 8, 1.383),
        ("Venus", 3, 8, 1.2),
        ("Mars", 4, 10, 0.524),
        ("Jupiter", 5, 10, 0.083),
        ("Saturn", 6, 10, 0.034),
        ("Uranus", 7, 6, 0.012),
        ("Neptune", 8, 6, 0.007),
        ("Pluto", 9, 4, 0.004),
        ("Rahu", 10, 0, -0.013),
        ("Lilith", 12, 0, 0.113),
    ],
    dtype=[("name", "S12"), ("swe_id", "i4"), ("orb", "f8"), ("speed", "f8")],
)

# Structured array of major aspects (harmonics 2 and 3): Conjunction,
# Semi-sextile, Sextile, Square, Trine, Quincunx and Opposition,
# their value and their coefficient for the calculation of the orb
aspects = np.array(
    [
        ("Conjunction", 0, 1),
        ("Semi-sextile", 30, 1 / 6),
        ("Sextile", 60, 1 / 3),
        ("Square", 90, 1 / 2),
        ("Trine", 120, 2 / 3),
        ("Quincunx", 150, 5 / 6),
        ("Opposition", 180, 1),
    ],
    dtype=[("name", "S12"), ("angle", "f8"), ("coef", "f8")],
)


# List of signs for body position
signs = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def vectorized_calc(jdate, swe_ids):
    """
    Perform vectorized calculations using the swisseph library.

    Args:
        jdate (float): Julian date.
        swe_ids (numpy.ndarray): Array of Swiss Ephemeris IDs.

    Returns:
        numpy.ndarray: Array of calculated results.
    """
    results = np.empty((len(swe_ids), 4))
    for idx, id in np.ndenumerate(swe_ids):
        results[idx] = swe.calc_ut(jdate, id)[0][:4]
    return results


def planets_props(jdate, swe_ids=bodies["swe_id"]):
    """
    Calculate the properties of celestial bodies for a given Julian date.

    Args:
        jdate (float): Julian date.
        swe_ids (numpy.ndarray, optional): Array of Swiss Ephemeris IDs.
            Defaults to the 'swe_id' field of the 'bodies' array.

    Returns:
        numpy.ndarray: Array of celestial body properties.
    """
    props = vectorized_calc(jdate, swe_ids)
    return np.rec.fromarrays(
        [swe_ids, props[:, 0], props[:, 1], props[:, 2], props[:, 3]],
        names=["swe_id", "lon", "lat", "vlon", "vlat"],
    )


class AstroDataWrapper:
    """
    Wrapper class for astrological data arrays.

    Attributes:
        data (numpy.ndarray): Array of astrological data.
    """

    def __init__(self, data):
        self.data = data

    def get(self, field):
        """
        Get a specific field from the astrological data array.

        Args:
            field (str or int): Name of the field or the Swiss Ephemeris ID.

        Returns:
            numpy.ndarray: Array of values for the specified field or body.
        """

        return self.data[field]

    def dtype(self):
        """
        Get the data type of the astrological data array.

        Returns:
            numpy.dtype: Data type of the array.
        """
        return self.data.dtype


class BodiesData(AstroDataWrapper):
    """
    Wrapper class for celestial bodies data.
    """

    def get(self, field):
        """
        Get a specific field from the astrological data array.

        Args:
            field (str or int): Name of the field or the Swiss Ephemeris ID.

        Returns:
            numpy.ndarray: Array of values for the specified field or body.
        """
        if isinstance(field, str):
            return self.data[field]
        elif isinstance(field, int):
            return self.data[self.data["swe_id"] == field]
        else:
            raise ValueError("Invalid field type. Expected str or int.")

    def name(self, swe_id=None):
        """
        Get the names of the celestial bodies.

        Args:
            swe_id (int, optional): The Swiss Ephemeris ID of the celestial body.
                If provided, returns the name of the specific body.
                If not provided, returns the names of all bodies.

        Returns:
            str | numpy.ndarray: The name of the specific celestial body if swe_id is provided,
                                    or an array of all celestial body names if swe_id is not provided.
        """

        if swe_id is None:
            return utf_8(self.data["name"])
        else:
            return utf_8(self.data["name"][self.data["swe_id"] == swe_id][0])

    def swe_id(self):
        """
        Get the Swiss Ephemeris IDs of the celestial bodies.

        Returns:
            numpy.ndarray: Array of Swiss Ephemeris IDs.
        """
        return self.data["swe_id"]

    def orb(self):
        """
        Get the orbs of the celestial bodies.

        Returns:
            numpy.ndarray: Array of orbs.
        """
        return self.data["orb"]

    def speed(self, swe_id=None):
        """
        Get the speeds of the celestial bodies.

        Args:
            swe_id (int, optional): The Swiss Ephemeris ID of the celestial body.
                If provided, returns the speed of the specific body.
                If not provided, returns the speeds of all bodies.

        Returns:
            float | numpy.ndarray: The speed of the specific celestial body if swe_id is provided,
                                    or an array of speeds of all celestial bodies if swe_id is not provided.
        """
        if swe_id is None:
            return self.data["speed"]
        else:
            return self.data["speed"][self.data["swe_id"] == swe_id][0]


class AspectsData(AstroDataWrapper):
    """
    Wrapper class for aspects data.
    """

    def name(self, i_asp=None):
        """
        Get the names of the aspects.

        Returns:
            numpy.ndarray: Array of aspect names.
        """
        return utf_8(self.data["name"])

    def angle(self):
        """
        Get the angles of the aspects.

        Returns:
            numpy.ndarray: Array of aspect angles.
        """
        return self.data["angle"]

    def coef(self):
        """
        Get the coefficients of the aspects.

        Returns:
            numpy.ndarray: Array of aspect coefficients.
        """
        return self.data["coef"]


# Create instances of the wrapper classes
bodies_data = BodiesData(bodies)
aspects_data = AspectsData(aspects)
