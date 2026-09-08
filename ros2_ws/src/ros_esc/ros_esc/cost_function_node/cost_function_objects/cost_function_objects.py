"""This script holds classes that describe cost function
objects for use in experiments. If the user wants to use one
of these cost function classes, they must specify the filepath
to this python script, and give the appropriate name to the
class they want to select in the cost function configuration
file. Then within this config file, they can specify various
parameters.
"""

from abc import ABC, abstractmethod
import numpy as np
from ros_esc.config_parsing import parse_sympy_expression
from ros_esc.cost_function_node.light_brightness import source_intensity_lumens

# pylint: disable=too-few-public-methods
class CostFunction(ABC):
    """Defines function calls needed from cost function objects.

    Every cost function class needs to have the cost
    output method. This is the method called by the cost function
    node to operate on the input values it receives. The cost function
    node will always give the same two variables as inputs:

    time (float): current time
        (either simulation or real time)
    sensor_transform (4x4 matrix): transformation matrix describing
        the position and orientation of the sensor frame represented
        in the global frame's axes

    This method will output the cost value for this sensor:
    output = cost value

    Class Methods:
        cost_output: gives the output of the cost function
        with call signature cost_output(time, sensor_transform)

    Note the cost ouput method should be the last method defined
    for the object, and it must end with this specific line of code:
    "return output". This is because this class will be parsed into
    a string for experiment documentation, and the parser is looking
    for the specific line "return output" to denote the end of the code
    describing this object.
    """

    def source_score(self, cost_value):
        """Return a normalized source score when the model exposes endpoints."""

        del cost_value
        return float("nan")

    @abstractmethod
    def cost_output(self, time, sensor_transform):
        """Every cost function must have an output function.

        This output function must depend on time, and the sensor's
        transformation matrix. This method will output the cost value:

        output = cost value
        """

        # pylint: disable=unnecessary-pass
        pass # This is an abstract method, no implementation here.

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
class Position_Based_Sympy_Expression(CostFunction):
    """This class allows for a position based sympy expression to be used as a cost function."""

    def __init__(self, params):
        """This initializes the object.

        The sympy expression should be defined in the config file as a dictionary
        named params in the following format. The function key should contain the
        cost function expressed symbolically as a string. The symbols key should
        match the one shown below, all cost functions will be functions of position
        and time. Finally, the substitutions key is optional, this can be used to
        define a dictionary of variables that will get substituted into the main
        expression. These variables may be defined as ints or floats, or they may
        contain more expressions expressed as strings.

        "params":{
            "function": {cost_function_expressed_symbolically_as_a_string},
            "symbols": ["t", "x", "y", "z"],
            "substitutions":{
                "substitution_1": float
                "substitution_2": {expression_string}
                etc...
            }
        }
        """

        # Create a lambda function with sympy
        # pylint: disable=unused-variable
        self.cost_function, self.cost_expression = parse_sympy_expression(params)

    def cost_output(self, time, sensor_transform):
        """This operates on input arguments and produces a cost value."""

        # Extract the sensor's position from the transformation matrix
        x = sensor_transform[0][3]
        y = sensor_transform[1][3]
        z = sensor_transform[2][3]

        # Calculate the cost value with the expression
        output = self.cost_function(time, x, y, z)

        return output

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
class Photoresistor_Interpolated_Map(CostFunction):
    """This creates an interpolated map of photoresistor data to be used as a cost function."""

    def __init__(self, params):
        """This initializes the object.

        The interpolated map should be defined in the config file as a dictionary
        named params in the following format. The mode key is how the user selects if
        they would like to return a resistance, or voltage cost value based off of
        experimentally collected data. This node uses a quadratic cost function based off
        of the resistance, however if the user desires to work with voltage instead,
        the object will convert its final resistance value into a voltage reading before
        returning the result. Note that the voltage reading increases when the resistance
        falls, thus to ensure our optimization problem is a minimization problem,
        we multiply the voltage value by negative one.

        The x_optimal and y_optimal keys are used to set the (x, y) position of the light
        source in the environment. The scale map key is optional, this allows the user to
        scale the size of the interpolated map by adjusting the radius variable. Finally,
        the apply adc key is optional, it allows the user to apply an analog to digital
        conversion to the computed cost value to mimic a reading one would get from using
        an Arduino board to capture data.
        
        The maximum resistance value for this interpolated map is 337260 Ohms, the minimum
        resistance value is 100 Ohms. There is an inverse relationship between voltage and
        resistance, as resistance rises, the voltage value decreases. Therefore at the max
        resistance value, the corresponding voltage is about 0.004 V, while at the min
        resistance value, the corresponding voltage is approximately 4.0 V. 
        
        Note that all voltage values are multiplied by -1 when returned as an output to
        ensure that our cost values relate to a minimization problem. Therefore the
        minimum cost value which relates to the light source corresponds to the lowest
        resistance value, and the most negative voltage value.

        "params":{
            "mode": string,
            "scale_map": float,
            "apply_adc": boolean,
            "x_optimal": float,
            "y_optimal": float,
        }
        """

        # Make assertions
        warn_msg = "There must be a 'mode' key in the params dictionary."
        assert "mode" in params, warn_msg
        warn_msg = "The 'mode' key must refer to either 'Resistance' or 'Voltage'."
        assert params["mode"] in ["Resistance", "Voltage"]
        warn_msg = "There must be a 'x_optimal' key in the params dictionary."
        assert "x_optimal" in params, warn_msg
        warn_msg = "There must be a 'y_optimal' key in the params dictionary."
        assert "y_optimal" in params, warn_msg

        # Select the desired mode for this object
        self.mode = params["mode"]
        # Set the desired position of the light source in the environment
        self.source_position = [params["x_optimal"], params["y_optimal"]]
        # Set the maximum value of photoresistor resistance
        self.max_value = 337260 # in ohms
        # Set the minimum value of photoresistor resistance
        self.min_value = 100 # in ohms
        # Set the scale of the interpolated map
        if "scale_map" in params:
            self.scale = params["scale_map"]
        else:
            self.scale = 1.0
        # Determine if we apply an ADC conversion to the cost value
        if "apply_adc" in params:
            self.apply_adc = params["apply_adc"]
        else:
            self.apply_adc = False

        # Our arduino uno we use to collect photoresistor readings only has a 10 bit
        # voltage resolution this means it can only represent an input voltage into
        # 1024 distinct voltage values. This means that we can only ever see 1024
        # distinct readings from the photoresistor. These values are computed
        # in the list below.

        # Define a list to hold the distict resistance readings we could get
        distinct_resistance_list = []
        # Calculate the resistance of the two resistors
        # we have wired in series with the photoresistor
        series_res = 337260 / (5/0.0049 - 1) # in ohms
        # Loop over all 1024 distinct possibilities
        for i in range(1023):
            # Add a resistance value to the list
            distinct_resistance_list.append(series_res*(5 / ((i+1)*0.0049) - 1))

        # Note this list is sorted from higher resistance values to lower ones
        # Every time we calculate a resistance value with the curve fit, we may then
        # match it with the closest resistance value from the above list to best mimic
        # the reading we would get from the circuit setup in real life
        self.distinct_list = distinct_resistance_list

    def match_reading(self, resistance):
        """This finds the closest possible reading to match the computed resistance value."""

        # Define a variable to track the error
        error = None
        # Loop over the list of distinct readings
        for index, value in enumerate(self.distinct_list):
            # Calculate the difference
            diff = np.abs(resistance - value)

            # If this is the first iteration
            if error is None:
                # Save the error
                error = diff

            # Otherwise, if our error increased compared to the previous iteration
            if diff > error:
                # Assign the resistance to the previous entry in
                # the list where the error was the smallest
                resistance = self.distinct_list[index-1]
                # We can stop iterating at this point
                break

        return resistance

    def curve_fit(self, radius, beta):
        """This function calculates the resistance using the resistance curve fit."""

        # Define quadratic curve fit coefficients
        a = 8.28082113e3
        b = 7.90425287
        c = 4.42130406e2
        d = 5.36416164e-13
        e = 1.68542637e-16
        f = 2.18515692e-18

        # Define the quadratic curve fit function for resistance
        resistance = a*radius**2 + b*beta**2 + c*radius*beta + d*radius + e*beta + f

        # Ensure we do not exceed the maximum resistance value
        if resistance > self.max_value:
            resistance = self.max_value

        # Ensure we do not go lower than the minimum resistance value
        if resistance < self.min_value:
            resistance = self.min_value

        # If we must match the resistance value we calculated
        # with one of the possible distinct readings
        if self.apply_adc:
            resistance = self.match_reading(resistance)

        return resistance

    def convert_resistance_to_voltage(self, resistance):
        """This converts a resistance reading into a voltage reading."""

        # Voltage = 5 / (Resistance / 330 + 1)
        voltage = 5 / (resistance / 330 + 1)
        # Multiply by negative one to ensure we have a minimization problem
        voltage *= -1

        return voltage

    def source_score(self, cost_value):
        """Normalize a post-noise cost using the model's resistance limits."""

        dark_cost = float(self.max_value)
        near_cost = float(self.min_value)
        if self.mode == "Voltage":
            dark_cost = self.convert_resistance_to_voltage(dark_cost)
            near_cost = self.convert_resistance_to_voltage(near_cost)
        denominator = near_cost - dark_cost
        if not np.isfinite(cost_value) or abs(denominator) <= 1e-15:
            return float("nan")
        return float(np.clip((cost_value - dark_cost) / denominator, 0.0, 1.0))

    def cost_output(self, time, sensor_transform):
        """This operates on input arguments and produces a cost value."""

        # Extract the sensor's position from the transformation matrix
        x = sensor_transform[0][3]
        y = sensor_transform[1][3]

        # Calculate the vector connecting the sensor to the source in the XY plane
        vec_sensor_to_source = [self.source_position[0] - x, self.source_position[1] - y]
        # Calculate the radius from the source in the 2D XY plane
        radius = np.linalg.norm(vec_sensor_to_source)

        # Get the unit vector of the sensor frame's x axis described in the global coordinates
        intermediate_step = np.matmul(sensor_transform, np.array([1, 0, 0, 0]).T)
        # Collect only the first row, and the first two elements
        vec_sensor_x_axis = intermediate_step[:2]

        # Compute the dot product of these two vectors
        dot_prod = np.dot(vec_sensor_to_source, vec_sensor_x_axis)
        # The dot product equals the magnitude of these
        # two vectors times the cosine of the angle between them
        beta = np.arccos(
            dot_prod / (np.linalg.norm(vec_sensor_to_source) * np.linalg.norm(vec_sensor_x_axis))
        )
        # Keep the magnitude of this result, convert beta to degrees
        beta = np.abs(beta) * 180 / np.pi
        if beta > 180:
            beta = 360 - beta

        # Get the output resistance, note we divide the radius by the scale
        # factor here if we want to adjust the radius scale of this interpolation map
        output = self.curve_fit(radius/self.scale, beta)

        # If we have selected the voltage mode
        if self.mode == "Voltage":
            output = self.convert_resistance_to_voltage(output)

        return output

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
class Multi_Light_Source_Cost(CostFunction):
    """Multi-light photoresistor cost using the rotating sensor direction."""

    def __init__(self, params):
        """Initialize a multi-light photoresistor cost map.

        Parameters:
            mode: "Resistance" or "Voltage", default "Voltage".
            scale_map: radius scaling factor for the fitted curve.
            apply_adc: if true, quantize the aggregate resistance reading.
            reference_intensity_lumens: fitted-curve reference light intensity.
            light_sources: x, y, brightness_percent (or legacy intensity_lumens).
        """

        self.mode = params.get("mode", "Voltage")
        if self.mode not in ["Resistance", "Voltage"]:
            raise ValueError("mode must be 'Resistance' or 'Voltage'.")

        self.scale = float(params.get("scale_map", 1.0))
        if self.scale <= 0:
            raise ValueError("scale_map must be greater than 0.")

        self.apply_adc = bool(params.get("apply_adc", False))
        self.reference_intensity_lumens = float(
            params.get("reference_intensity_lumens", 1000.0)
        )
        if self.reference_intensity_lumens <= 0:
            raise ValueError("reference_intensity_lumens must be greater than 0.")

        self.max_value = 337260 # in ohms
        self.min_value = 100 # in ohms

        self.light_sources = self._normalize_light_sources(
            params.get("light_sources", [])
        )
        self.distinct_list = self._build_distinct_resistance_list()

    def _build_distinct_resistance_list(self):
        """Build ADC-like resistance readings used by the photoresistor model."""

        distinct_resistance_list = []
        series_res = 337260 / (5/0.0049 - 1) # in ohms
        for i in range(1023):
            distinct_resistance_list.append(series_res*(5 / ((i+1)*0.0049) - 1))

        return distinct_resistance_list

    def _normalize_light_sources(self, light_sources):
        """Validate and normalize a light-source list."""

        if light_sources is None:
            light_sources = []
        if not isinstance(light_sources, list):
            raise TypeError("light_sources must be a list.")

        normalized_sources = []
        for source_idx, source in enumerate(light_sources, start=1):
            if not isinstance(source, dict):
                raise TypeError(f"light source {source_idx} must be a dictionary.")
            try:
                x_pos = float(source["x"])
                y_pos = float(source["y"])
                intensity_lumens = source_intensity_lumens(source)
            except KeyError as exc:
                raise KeyError(
                    f"light source {source_idx} is missing required key {exc}."
                ) from exc
            if intensity_lumens < 0:
                raise ValueError(
                    f"light source {source_idx} intensity_lumens must be >= 0."
                )
            normalized_sources.append({
                "x": x_pos,
                "y": y_pos,
                "intensity_lumens": intensity_lumens,
            })
            if source.get("brightness_percent") is not None:
                normalized_sources[-1]["brightness_percent"] = float(
                    source["brightness_percent"]
                )

        return normalized_sources

    def configure_light_sources(self, light_source_count, light_sources):
        """Override configured lights from launch-time light-source arguments."""

        if light_source_count is None:
            return
        light_source_count = int(light_source_count)
        if light_source_count < 0:
            raise ValueError("light_source_count must be >= 0.")
        if light_source_count > len(light_sources):
            raise ValueError(
                f"light_source_count={light_source_count} exceeds "
                f"available launch light slots={len(light_sources)}."
            )

        selected_sources = []
        for source_idx in range(light_source_count):
            source = light_sources[source_idx]
            missing_keys = [
                key for key, value in source.items()
                if value is None and (
                    key in ("x", "y") or (
                        key == "intensity_lumens"
                        and source.get("brightness_percent") is None
                    )
                )
            ]
            if missing_keys:
                raise ValueError(
                    f"light source {source_idx + 1} missing launch values: "
                    + ", ".join(missing_keys)
                )
            selected_sources.append(source)

        self.light_sources = self._normalize_light_sources(selected_sources)

    def _match_reading(self, resistance):
        """Find the closest ADC-like resistance reading."""

        error = None
        for index, value in enumerate(self.distinct_list):
            diff = np.abs(resistance - value)

            if error is None:
                error = diff

            if diff > error:
                resistance = self.distinct_list[index-1]
                break

        return resistance

    def _curve_fit(self, radius, beta):
        """Calculate resistance from the existing photoresistor curve fit."""

        a = 8.28082113e3
        b = 7.90425287
        c = 4.42130406e2
        d = 5.36416164e-13
        e = 1.68542637e-16
        f = 2.18515692e-18

        resistance = a*radius**2 + b*beta**2 + c*radius*beta + d*radius + e*beta + f
        resistance = min(resistance, self.max_value)
        resistance = max(resistance, self.min_value)

        return resistance

    def _convert_resistance_to_voltage(self, resistance):
        """Convert resistance into negative divider voltage for minimization."""

        voltage = 5 / (resistance / 330 + 1)
        voltage *= -1

        return voltage

    def _sensor_x_axis(self, sensor_transform):
        """Return the sensor x-axis direction in global XY coordinates."""

        intermediate_step = np.matmul(sensor_transform, np.array([1, 0, 0, 0]).T)
        return intermediate_step[:2]

    def _source_radius_beta(self, sensor_transform, source):
        """Compute source radius and angle from the rotating sensor direction."""

        x_pos = sensor_transform[0][3]
        y_pos = sensor_transform[1][3]
        vec_sensor_to_source = np.array(
            [source["x"] - x_pos, source["y"] - y_pos],
            dtype=float,
        )
        radius = np.linalg.norm(vec_sensor_to_source)
        if radius <= 0:
            return 0.0, 0.0

        vec_sensor_x_axis = self._sensor_x_axis(sensor_transform)
        sensor_axis_norm = np.linalg.norm(vec_sensor_x_axis)
        if sensor_axis_norm <= 0:
            return radius, 0.0

        dot_prod = np.dot(vec_sensor_to_source, vec_sensor_x_axis)
        cos_beta = dot_prod / (radius * sensor_axis_norm)
        cos_beta = np.clip(cos_beta, -1.0, 1.0)
        beta = np.abs(np.arccos(cos_beta)) * 180 / np.pi
        if beta > 180:
            beta = 360 - beta

        return radius, beta

    def _source_conductance_delta(self, sensor_transform, source):
        """Compute one source contribution as a scaled conductance delta."""

        if source["intensity_lumens"] <= 0:
            return 0.0

        radius, beta = self._source_radius_beta(sensor_transform, source)
        source_resistance = self._curve_fit(radius/self.scale, beta)
        dark_conductance = 1 / self.max_value
        source_conductance = 1 / source_resistance
        conductance_delta = max(source_conductance - dark_conductance, 0.0)
        intensity_scale = source["intensity_lumens"] / self.reference_intensity_lumens

        return conductance_delta * intensity_scale

    def source_score(self, cost_value):
        """Normalize a post-noise cost using the model's resistance limits."""

        dark_cost = float(self.max_value)
        near_cost = float(self.min_value)
        if self.mode == "Voltage":
            dark_cost = self._convert_resistance_to_voltage(dark_cost)
            near_cost = self._convert_resistance_to_voltage(near_cost)
        denominator = near_cost - dark_cost
        if not np.isfinite(cost_value) or abs(denominator) <= 1e-15:
            return float("nan")
        return float(np.clip((cost_value - dark_cost) / denominator, 0.0, 1.0))

    def cost_output(self, time, sensor_transform):
        """Evaluate the multi-light photoresistor cost."""

        del time
        total_conductance = 1 / self.max_value
        for source in self.light_sources:
            total_conductance += self._source_conductance_delta(sensor_transform, source)

        output = 1 / total_conductance
        output = min(output, self.max_value)
        output = max(output, self.min_value)

        if self.apply_adc:
            output = self._match_reading(output)

        if self.mode == "Voltage":
            output = self._convert_resistance_to_voltage(output)

        return output
