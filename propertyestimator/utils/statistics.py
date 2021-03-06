"""
A collection of classes for loading and manipulating statistics data files.
"""
import copy
import math
from enum import Enum
from io import StringIO

import numpy as np
import pandas as pd
from simtk import unit


class ObservableType(Enum):
    """The supported statistics which may be extracted / stored
    in statistics data files.
    """

    PotentialEnergy = 'PotentialEnergy'
    KineticEnergy = 'KineticEnergy'
    TotalEnergy = 'TotalEnergy'
    Temperature = 'Temperature'
    Volume = 'Volume'
    Density = 'Density'
    Enthalpy = 'Enthalpy'


class StatisticsArray:
    """
    A data object for storing and retrieving statistics generated by an OpenMM simulation.
    """

    def __init__(self, potential_energies, kinetic_energies, total_energies,
                 temperatures, volumes, densities, enthalpies):
        """Constructs a new StatisticsArray object.

        Parameters
        ----------
        """

        self._internal_data = {
            ObservableType.PotentialEnergy: potential_energies,
            ObservableType.KineticEnergy: kinetic_energies,
            ObservableType.TotalEnergy: total_energies,
            ObservableType.Temperature: temperatures,
            ObservableType.Volume: volumes,
            ObservableType.Density: densities,
            ObservableType.Enthalpy: enthalpies,
        }

    def __len__(self):
        """Get the number of data items in the array.

        Returns
        -------
        int
            The number of data items in the array.
        """
        return len(self._internal_data[ObservableType.PotentialEnergy])

    def get_observable(self, observable_type):
        """Return the data for a given observable.

        Parameters
        ----------
        observable_type: ObservableType
            The type of observable to retrieve.

        Returns
        -------
        np.ndarray, shape=(len(self)) dtype=unit.Quantity
            The data.
        """

        if not self.has_observable(observable_type):
            return None

        return self._internal_data[observable_type]

    def has_observable(self, observable_type):
        """Return the data for a given statistic.

        Parameters
        ----------
        observable_type: ObservableType
            The type of observable to retrieve.

        Returns
        -------
        bool
            True if data for the `observable_type` is available.
        """
        return observable_type in self._internal_data

    def save_as_pandas_csv(self, file_path):
        """Saves the `StatisticsArray` to a pandas csv file.

        Parameters
        ----------
        file_path: str
            The file path to save the csv file to.
        """

        data = np.array([
            self._internal_data[ObservableType.PotentialEnergy] / unit.kilojoule_per_mole,
            self._internal_data[ObservableType.KineticEnergy] / unit.kilojoule_per_mole,
            self._internal_data[ObservableType.TotalEnergy] / unit.kilojoule_per_mole,
            self._internal_data[ObservableType.Temperature] / unit.kelvin,
            self._internal_data[ObservableType.Volume] / unit.nanometer**3,
            self._internal_data[ObservableType.Density] / unit.gram * unit.milliliter,
            self._internal_data[ObservableType.Enthalpy] / unit.kilojoule_per_mole])

        data = data.transpose()

        columns = [
            "Potential Energy (kJ/mole)",
            "Kinetic Energy (kJ/mole)",
            "Total Energy (kJ/mole)",
            "Temperature (K)",
            "Box Volume (nm^3)",
            "Density (g/mL)",
            "Enthalpy (kJ/mole)"
        ]

        data_frame = pd.DataFrame(data=data, columns=columns)
        data_frame.to_csv(file_path)

    @classmethod
    def from_openmm_csv(cls, file_path, pressure=None):
        """Creates a new `StatisticsArray` object from an openmm csv file.

        Parameters
        ----------
        file_path: str
            The file path to the csv file.
        pressure: unit.Quantity, optional
            The pressure at which the statisitcs in the csv file were sampled,
            if sampling was performed in a constant pressure ensemble.
        Returns
        -------

        """
        file_contents = None

        with open(file_path, 'r') as file:

            file_contents = file.read()

            if len(file_contents) < 1:
                raise ValueError('The statistics file is empty.')

            file_contents = file_contents[1:]

        string_object = StringIO(file_contents)
        data = pd.read_csv(string_object)

        if 'Potential Energy (kJ/mole)' not in data:
            raise ValueError('The statistics file does not contain a Potential Energy column.')

        potential_energies = np.array(data['Potential Energy (kJ/mole)']) * unit.kilojoule / unit.mole

        if 'Kinetic Energy (kJ/mole)' not in data:
            raise ValueError('The statistics file does not contain a Kinetic Energy column.')

        kinetic_energies = np.array(data['Kinetic Energy (kJ/mole)']) * unit.kilojoule / unit.mole

        if 'Total Energy (kJ/mole)' not in data:
            raise ValueError('The statistics file does not contain a Total Energy column.')

        total_energies = np.array(data['Total Energy (kJ/mole)']) * unit.kilojoule / unit.mole

        if 'Temperature (K)' not in data:
            raise ValueError('The statistics file does not contain a Temperature column.')

        temperatures = np.array(data['Temperature (K)']) * unit.kelvin

        if 'Box Volume (nm^3)' not in data:
            raise ValueError('The statistics file does not contain a Box Volume column.')

        volumes = np.array(data['Box Volume (nm^3)']) * unit.nanometer * unit.nanometer * unit.nanometer

        if 'Density (g/mL)' not in data:
            raise ValueError('The statistics file does not contain a Density column.')

        densities = np.array(data['Density (g/mL)']) * unit.gram / unit.milliliter

        enthalpies = None

        if pressure is not None:
            enthalpies = total_energies + volumes * pressure * unit.AVOGADRO_CONSTANT_NA

        return cls(potential_energies, kinetic_energies, total_energies,
                   temperatures, volumes, densities, enthalpies)

    @classmethod
    def from_pandas_csv(cls, file_path):
        """Creates a new `StatisticsArray` object from an pandas csv file.

        Parameters
        ----------
        file_path: str
            The file path to the csv file.
        """
        file_contents = None

        with open(file_path, 'r') as file:

            file_contents = file.read()

            if len(file_contents) < 1:
                raise ValueError('The statistics file is empty.')

        string_object = StringIO(file_contents)
        data = pd.read_csv(string_object)

        if 'Potential Energy (kJ/mole)' not in data:
            raise ValueError('The statistics file does not contain a Potential Energy column.')

        potential_energies = np.array(data['Potential Energy (kJ/mole)']) * unit.kilojoule / unit.mole

        if 'Kinetic Energy (kJ/mole)' not in data:
            raise ValueError('The statistics file does not contain a Kinetic Energy column.')

        kinetic_energies = np.array(data['Kinetic Energy (kJ/mole)']) * unit.kilojoule / unit.mole

        if 'Total Energy (kJ/mole)' not in data:
            raise ValueError('The statistics file does not contain a Total Energy column.')

        total_energies = np.array(data['Total Energy (kJ/mole)']) * unit.kilojoule / unit.mole

        if 'Temperature (K)' not in data:
            raise ValueError('The statistics file does not contain a Temperature column.')

        temperatures = np.array(data['Temperature (K)']) * unit.kelvin

        if 'Box Volume (nm^3)' not in data:
            raise ValueError('The statistics file does not contain a Box Volume column.')

        volumes = np.array(data['Box Volume (nm^3)']) * unit.nanometer * unit.nanometer * unit.nanometer

        if 'Density (g/mL)' not in data:
            raise ValueError('The statistics file does not contain a Density column.')

        densities = np.array(data['Density (g/mL)']) * unit.gram / unit.milliliter

        enthalpies = None

        if 'Enthalpy (kJ/mole)' in data:
            enthalpies = np.array(data['Enthalpy (kJ/mole)']) * unit.kilojoule_per_mole

        return cls(potential_energies, kinetic_energies, total_energies,
                   temperatures, volumes, densities, enthalpies)

    @classmethod
    def from_statistics_array(cls, existing_instance, data_indices=None):
        """Creates a new `StatisticsArray` from an existing array. If
        a set of data indices are provided, only a subset of data will
        be copied across from the existing instance.

        Parameters
        ----------
        existing_instance: `StatisticsArray`
            The existing array to clone
        data_indices: list of int, optional
            A set of indices, which indicate which data points to copy
            from the original objext. If None, all data points will be
            copied.

        Returns
        -------
        `StatisticsArray`
            The created array object.
        """

        potential_energies = copy.deepcopy(existing_instance.get_observable(ObservableType.PotentialEnergy))
        kinetic_energies = copy.deepcopy(existing_instance.get_observable(ObservableType.KineticEnergy))
        total_energies = copy.deepcopy(existing_instance.get_observable(ObservableType.TotalEnergy))
        temperatures = copy.deepcopy(existing_instance.get_observable(ObservableType.Temperature))
        volumes = copy.deepcopy(existing_instance.get_observable(ObservableType.Volume))
        densities = copy.deepcopy(existing_instance.get_observable(ObservableType.Density))
        enthalpies = copy.deepcopy(existing_instance.get_observable(ObservableType.Enthalpy))

        return_object = StatisticsArray(potential_energies[data_indices],
                                        kinetic_energies[data_indices],
                                        total_energies[data_indices],
                                        temperatures[data_indices],
                                        volumes[data_indices],
                                        densities[data_indices],
                                        enthalpies[data_indices])

        return return_object


def bootstrap(bootstrap_function, iterations=200, relative_sample_size=1.0, data_sub_counts=None, **data_kwargs):
    """Performs bootstrapping on a data set to calculate the
    average value, and the standard error in the average,
    bootstrapping.

    Parameters
    ----------
    bootstrap_function: function
        The function to evaluate at each bootstrap iteration. The function
        should take a kwargs array as input, and return a float.
    iterations: int
        The number of bootstrap iterations to perform.
    relative_sample_size: float
        The percentage sample size to bootstrap over, relative to the
        size of the full data set.
    data_sub_counts: np.ndarray, optional
        If the data being bootstrapped contains arrays of concatenated sub data
        (such as when reweighting), this variable can be used to the number of
        items which belong to each subset. Data is then sampled with replacement
        so that the bootstrap sample contains the correct proportion of data from
        each subset.

        If the data to bootstrap is of the form [x0, x1, x2, y0, y1] for example,
        then `data_sub_counts=[3, 2]` and a possible sample may look like
        [x0, x0, x2, y0, y0], but never [x0, x1, y0, y1, y1].
    data_kwargs: np.ndarray, shape=(num_frames, num_dimensions), dtype=float
        A key words dictionary of the data which will be passed to the
         bootstrap function. Each kwargs argument should be a numpy array.

    Returns
    -------
    float
        The average of the data.
    float
        The uncertainty in the average.
    """

    if len(data_kwargs) is 0:
        raise ValueError('There is no data to bootstrap')

    # Make a copy of the data so we don't accidentally destroy anything.
    data_to_bootstrap = {}
    data_size = None

    for keyword in data_kwargs:

        assert isinstance(data_kwargs[keyword], np.ndarray)
        data_to_bootstrap[keyword] = np.array(data_kwargs[keyword])

        if data_size is None:
            data_size = len(data_kwargs[keyword])
        else:
            assert data_size == len(data_kwargs[keyword])

    if data_sub_counts is None:
        data_sub_counts = np.array([data_size])

    assert data_sub_counts.sum() == data_size

    average_values = np.zeros(iterations)

    for bootstrap_iteration in range(iterations):

        sample_data = {}

        for keyword in data_to_bootstrap:
            sample_data[keyword] = np.zeros(data_to_bootstrap[keyword].shape)

        start_index = 0

        for sub_count in data_sub_counts:

            # Choose the sample size as a percentage of the full data set.
            sample_size = min(math.floor(sub_count * relative_sample_size), sub_count)
            sample_indices = np.random.choice(sub_count, sample_size)

            for keyword in data_to_bootstrap:

                sub_data = data_to_bootstrap[keyword][start_index: start_index + sub_count]

                for index in range(sub_count):
                    sample_data[keyword][index + start_index] = sub_data[sample_indices][index]

            start_index += sub_count

        average_values[bootstrap_iteration] = bootstrap_function(**sample_data)

    average_value = bootstrap_function(**data_to_bootstrap)
    uncertainty = average_values.std()

    if isinstance(average_value, np.float32) or isinstance(average_value, np.float64):
        average_value = average_value.item()

    if isinstance(uncertainty, np.float32) or isinstance(uncertainty, np.float64):
        uncertainty = uncertainty.item()

    return average_value, uncertainty
