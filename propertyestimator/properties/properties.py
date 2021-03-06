"""
Properties base API.
"""

import uuid
from enum import IntFlag, unique, Enum

from propertyestimator.utils.serialization import TypedBaseModel


@unique
class PropertyPhase(IntFlag):
    """An enum describing the phase a property was collected in.
    """

    Undefined = 0x00
    Solid = 0x01
    Liquid = 0x02
    Gas = 0x04

    def __str__(self):
        """
        Returns
        ---
        str
            A string representation of the PropertyPhase enum
        """
        phases = '|'.join([phase.name for phase in PropertyPhase if self & phase])
        return phases

    def __repr__(self):
        """
        Returns
        ---
        str
            A string representation of the PropertyPhase enum
        """
        return str(self)


class Source(TypedBaseModel):
    """Container class for information about how a property was measured / calculated.

    .. todo:: Swap this out with a more general provenance class.
    """

    def __getstate__(self): return {}

    def __setstate__(self, state): pass


class MeasurementSource(Source):
    """Contains any metadata about how a physical property was measured by experiment.

    This class contains either the DOI and/or the reference, but must contain at
    least one as the observable must have a source, even if it was measured in lab.

    Attributes
    ----------
    doi : str or None, default None
        The DOI for the source, preferred way to identify for source
    reference : str
        The long form description of the source if no DOI is available, or more
        information is needed or wanted.
    """

    def __init__(self, doi='', reference=''):
        """Constructs a new MeasurementSource object.

        Parameters
        ----------
        doi : str or None, default None
            The DOI for the source, preferred way to identify for source
        reference : str
            The long form description of the source if no DOI is available, or more
            information is needed or wanted.
        """

        self.doi = doi
        self.reference = reference

    def __getstate__(self):

        return {
            'doi': self.doi,
            'reference': self.reference,
        }

    def __setstate__(self, state):

        self.doi = state['doi']
        self.reference = state['reference']


class CalculationSource(Source):
    """Contains any metadata about how a physical property was calculated.

    This includes at which fidelity the property was calculated at (e.g Direct
    simulation, reweighting, ...) in addition to the parameters which were
    used as part of the calculations.

    Attributes
    ----------
    fidelity : str
        The fidelity at which the property was calculated
    provenance : dict of str and Any
        A dictionary containing information about how the property was calculated.
    """

    def __init__(self, fidelity=None, provenance=None):
        """Constructs a new CalculationSource object.

        Parameters
        ----------
        fidelity : str
            The fidelity at which the property was calculated
        provenance : dict of str and Any
            A dictionary containing information about how the property was calculated.
        """

        self.fidelity = fidelity
        self.provenance = provenance

    def __getstate__(self):

        return {
            'fidelity': self.fidelity,
            'provenance': self.provenance,
        }

    def __setstate__(self, state):

        self.fidelity = state['fidelity']
        self.provenance = state['provenance']


class PropertyWorkflowOptions:
    """A set of convenience options used when creating
    estimation workflows.
    """

    class ConvergenceMode(Enum):
        """The available options for deciding when a workflow has converged.
        For now, these options include running until the computed uncertainty
        of a property is within a relative fraction of the measured uncertainty
        (`ConvergenceMode.RelativeUncertainty`) or is less than some absolute
        value (`ConvergenceMode.AbsoluteUncertainty`)."""

        # NoChecks = 'NoChecks'
        RelativeUncertainty = 'RelativeUncertainty'
        AbsoluteUncertainty = 'AbsoluteUncertainty'

    def __init__(self,
                 convergence_mode=ConvergenceMode.RelativeUncertainty,
                 relative_uncertainty_fraction=1.0, absolute_uncertainty=None):
        """Constructs a new DefaultPropertyWorkflowOptions object.

        Parameters
        ----------
        convergence_mode: PropertyWorkflowOptions.ConvergenceMode
            The mode which governs how workflows should decide when they have
            reached convergence.
        relative_uncertainty_fraction: float, optional
            If the convergence mode is set to `RelativeUncertainty`, then workflows
            will by default run simulations until the estimated uncertainty is less
            than

            `relative_uncertainty_fraction` * property_to_estimate.uncertainty
        absolute_uncertainty: simtk.unit.Quantity, optional
            If the convergence mode is set to `AbsoluteUncertainty`, then workflows
            will by default run simulations until the estimated uncertainty is less
            than the `absolute_uncertainty`
        """

        self.convergence_mode = convergence_mode

        self.absolute_uncertainty = absolute_uncertainty
        self.relative_uncertainty_fraction = relative_uncertainty_fraction

        if (self.convergence_mode is self.ConvergenceMode.RelativeUncertainty and
            self.relative_uncertainty_fraction is None):

            raise ValueError('The relative uncertainty fraction must be set when the convergence '
                             'mode is set to RelativeUncertainty.')

        if (self.convergence_mode is self.ConvergenceMode.AbsoluteUncertainty and
            self.absolute_uncertainty is None):

            raise ValueError('The absolute uncertainty must be set when the convergence '
                             'mode is set to AbsoluteUncertainty.')

    def __getstate__(self):

        return {
            'convergence_mode': self.convergence_mode,

            'absolute_uncertainty': self.absolute_uncertainty,
            'relative_uncertainty_fraction': self.relative_uncertainty_fraction
        }

    def __setstate__(self, state):

        self.convergence_mode = state['convergence_mode']

        self.absolute_uncertainty = state['absolute_uncertainty']
        self.relative_uncertainty_fraction = state['relative_uncertainty_fraction']


class PhysicalProperty(TypedBaseModel):
    """Represents the value of any physical property and it's uncertainty.

    It additionally stores the thermodynamic state at which the property
    was collected, the phase it was collected in, information about
    the composition of the observed system, and metadata about how the
    property was collected.
    """

    def __init__(self, thermodynamic_state=None, phase=PropertyPhase.Undefined,
                 substance=None, value=None, uncertainty=None, source=None):
        """Constructs a new PhysicalProperty object.

        Parameters
        ----------
        thermodynamic_state : ThermodynamicState
            The thermodynamic state that the property was measured in.
        phase : PropertyPhase
            The phase that the property was measured in.
        substance : Substance
            The composition of the substance that was measured.
        value: unit.Quantity
            The value of the measured physical property.
        uncertainty: unit.Quantity
            The uncertainty in the measured value.
        source: Source
            The source of this property.
        """
        self.id = str(uuid.uuid4())

        self.thermodynamic_state = thermodynamic_state
        self.phase = phase

        self.substance = substance

        self.value = value
        self.uncertainty = uncertainty

        self.source = source

    def __getstate__(self):

        return {
            'id': self.id,

            'thermodynamic_state': self.thermodynamic_state,
            'phase': self.phase,
    
            'substance': self.substance,
    
            'value': self.value,
            'uncertainty': self.uncertainty,
    
            'source': self.source,
        }

    def __setstate__(self, state):

        self.id = state['id']

        self.thermodynamic_state = state['thermodynamic_state']
        self.phase = state['phase']

        self.substance = state['substance']

        self.value = state['value']
        self.uncertainty = state['uncertainty']

        self.source = state['source']

    @property
    def temperature(self):
        """simtk.unit.Quantity or None: The temperature at which the property was collected."""
        return None if self.thermodynamic_state is None else self.thermodynamic_state.temperature

    @property
    def pressure(self):
        """simtk.unit.Quantity or None: The pressure at which the property was collected."""
        return None if self.thermodynamic_state is None else self.thermodynamic_state.pressure

    def set_value(self, value, uncertainty):
        """Set the value and uncertainty of this property.

        Parameters
        ----------
        value : simtk.unit.Quantity
            The value of the property.
        uncertainty : simtk.unit.Quantity
            The uncertainty in the properties value.
        """
        self.value = value
        self.uncertainty = uncertainty

    @staticmethod
    def get_default_workflow_schema(calculation_layer, options=None):
        """Returns the default workflow schema to use for
        a specific calculation layer.

        Parameters
        ----------
        calculation_layer: str
            The calculation layer which will attempt to execute the workflow
            defined by this schema.
        options: PropertyWorkflowOptions
            The options to use when setting up the default workflows.

        Returns
        -------
        WorkflowSchema
            The default workflow schema.
        """
        raise NotImplementedError()
