"""
An API for defining, storing, and loading collections of physical property data.
"""


class PhysicalPropertyDataSet(object):
    """
    A data set of physical property measurements / calculations.
    Contains functionality for merging multiple data sets and
    filtering existing ones.
    """

    def __init__(self):
        """
        Constructs a new PhysicalPropertyDataSet
        """
        self._properties = {}
        self._sources = []

    @property
    def properties(self):
        """
        dict(str, list(PhysicalProperty)): The property list which
        takes a substance as the key.
        """
        return self._properties

    @property
    def sources(self):
        """list of Source: The list of sources from which the properties were gathered"""
        return self._sources

    def merge(self, data_set):
        """Merge another data set into the current one.

        Parameters
        ----------
        data_set : PhysicalPropertyDataSet
            The secondary data set to merge into this one.
        """
        # TODO: Do we need to check whether merging the same data set here?
        for substance_hash in data_set.properties:

            if substance_hash not in self._properties:
                self._properties[substance_hash] = []

            self._properties[substance_hash].extend(
                data_set.properties[substance_hash])

        self._sources.extend(data_set.sources)

    def filter_by_function(self, filter_function):
        """Filter the data set using a given filter function.

        Parameters
        ----------
        filter_function : lambda
            The filter function.
        """

        # This works for now - if we wish to be able to undo a filter then
        # a 'filtered' list needs to be maintained separately to the main list.
        for substance_hash in self._properties:

            self._properties[substance_hash] = list(filter(
                filter_function, self._properties[substance_hash]))

    def filter_by_properties(self, types):
        """Filter the data set based on the type of property (e.g Density).

        Parameters
        ----------
        types : list of PropertyType
            The types of property which should be retained.

        Examples
        --------
        Filter the dataset to only contain densities and static dielectric constants

        >>> # Load in the data set of properties which will be used for comparisons
        >>> from propertyestimator.datasets import ThermoMLDataSet
        >>> data_set = ThermoMLDataSet.from_doi('10.1016/j.jct.2016.10.001')
        >>>
        >>> # Filter the dataset to only include densities measured between 130-260 K
        >>> from propertyestimator.properties import Density, DielectricConstant
        >>> data_set.filter_by_properties(types=[Density, DielectricConstant])
        """
        property_types = []

        for property_type in types:

            if isinstance(property_type, str):
                property_types.append(property_type)
            else:
                property_types.append(property_type.__name__)

        def filter_function(x):
            return x.type in property_types

        self.filter_by_function(filter_function)

    def filter_by_phases(self, phases):
        """Filter the data set based on the phase of the property (e.g Liquid).

        Parameters
        ----------
        phases : PropertyPhase
            The phase of property which should be retained.

        Examples
        --------
        Filter the dataset to only include liquid properties.

        >>> # Load in the data set of properties which will be used for comparisons
        >>> from propertyestimator.datasets import ThermoMLDataSet
        >>> data_set = ThermoMLDataSet.from_doi('10.1016/j.jct.2016.10.001')
        >>>
        >>> from propertyestimator.properties import PropertyPhase
        >>> data_set.filter_by_temperature(PropertyPhase.Liquid)
        """
        def filter_function(x):
            return x.phase & phases

        self.filter_by_function(filter_function)

    def filter_by_temperature(self, min_temperature, max_temperature):
        """Filter the data set based on a minimum and maximum temperature.

        Parameters
        ----------
        min_temperature : float
            The minimum temperature.
        max_temperature : float
            The maximum temperature.

        Examples
        --------
        Filter the dataset to only include properties measured between 130-260 K.

        >>> # Load in the data set of properties which will be used for comparisons
        >>> from propertyestimator.datasets import ThermoMLDataSet
        >>> data_set = ThermoMLDataSet.from_doi('10.1016/j.jct.2016.10.001')
        >>>
        >>> from simtk import unit
        >>> data_set.filter_by_temperature(min_temperature=130*unit.kelvin, max_temperature=260*unit.kelvin)
        """
        def filter_function(x):
            return min_temperature <= x.thermodynamic_state.temperature <= max_temperature

        self.filter_by_function(filter_function)

    def filter_by_components(self, number_of_components):
        """Filter the data set based on a minimum and maximum temperature.

        Parameters
        ----------
        number_of_components : int
            The allowed number of components in the mixture.

        Examples
        --------
        Filter the dataset to only include pure substance properties.

        >>> # Load in the data set of properties which will be used for comparisons
        >>> from propertyestimator.datasets import ThermoMLDataSet
        >>> data_set = ThermoMLDataSet.from_doi('10.1016/j.jct.2016.10.001')
        >>>
        >>> data_set.filter_by_components(number_of_components=1)
        """
        def filter_function(x):
            return x.substance.number_of_components == number_of_components

        self.filter_by_function(filter_function)
