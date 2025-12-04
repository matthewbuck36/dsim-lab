# Description

A photoresistor was used to assess the light intensity of the environment. A 
photoresistor's resistance varies with the amount of light that hits the surface
of the sensor. The sensor's resistance is inversely proportional to the light intensity
that it sees, thus as the light gets more intense, the photoresistor's resistance
goes down.

The photoresistor's resistance varies as a function of the distance from the light source,
and the amount of the sensor's surface that is facing the light source. We denote the distance
from the light source as a radius $r$, measured in meters. We assess the amount of the sensor's surface
facing the light source with an angle called $\beta$. The angle $\beta$ describes the angle
between the vector normal to the photoresistor's surface, and the vector from the sensor to the
light source. This can be seen in the figure given below. A $\beta$ value of zero means that
the entirety of the photoresistor's surface is facing the source, and as $\beta$ increases,
less of the photoresistor's surface is facing the source. These measurements were taken with a 
photoresistor wired in a circuit shown below.

![Beta angle diagram](/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/beta_angle_diagram.png)

![Photoresistor circuit diagram](/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/photoresistor_circuit_diagram.png)

An Arduino Uno board was used to sample voltage readings at the indicated point, then
calculated the photoresistor resistance using the following equations:

$$ I = V_{measured} / (330 \Omega) $$

$$ R_{photoresistor} = (5 - V_{measured})/ I $$

Note that the Arduino Uno has a 10 bit analog to digital converter, thus any sampled
voltage value must be represented by one of 1024 distinct possibilities. This means
that any resistance value must also be one of 1024 distinct possibilities.

Photoresistor Reference:
https://www.adafruit.com/product/161


## Python Plotting Script
Within this directory, there is a [python plotting script](/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/photoresistor_measurement_plots.py) which is responsible for generating the quadratic curve fit off of the experimental data recorded in this [csv file](/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/photoresistor_measurement_data.csv). This quadratic curve fit is of the form:

$$ R(r, \beta) = a*r^2 + b*\beta^2 + c*r*\beta + d*r + e*\beta + f $$

Note constants a through f are all positive real numbers. With this result an associated voltage value can be calculated with

$$ V(r, \beta) = \frac{5}{\frac{R(r,\beta)}{330} + 1}  $$

This plotting script generates a few heat maps of the resistance and voltage values at choice $\beta$ angles. This code also creates a two dimensional contour plot of the resistance as a function of radius and $\beta$.

![2D resistance contours](/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/figures/resistance_contours.png)

![2D voltage contours](/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/figures/voltage_contours.png)

## Quadratic Curve Fit Equation

This virtual light source cost function is a quadratic curve fit describing the photoresistor's resistance value (in ohms) as a function of the radius (in meters) of the sensor to the light source, and the angle $\beta$ describing how much of the photoresistor's surface is facing the light source. This cost function is additionally constrained by minimum and maximum resistance values of $R_{min} = 100$ and $R_{max} = 337260$. The virtual light source quadratic curve fit can be seen below.

$$ R(r, \beta) = (8.28082113e3)*r^2 + (7.90425287)*\beta^2 + (4.42130406e2)*r*\beta + (5.36416164e-13)*r + (1.68542637e-16)*\beta + 2.18515692e-18 $$

We then take this value and ensure the resistance falls within our constraints, setting the resistance value to the appropriate bound if it falls outside of this range

$$ R_{min} \leq R(r, \beta) \leq R_{max} $$

If the user wants to apply an ADC conversion on top of this calculated resistance value, they would match the computed result with the closest distinct resistance level in the following list. Note $\delta V = 0.0049$ volts, and $R_{a} = 330$ ohms is the resistance of the components wired in series in the circuit shown above.

$$ (R_{a} (\frac{5}{n*\delta V}-1))_{n=1}^{1024} $$

Once a resistance value has been computed based off of the quadratic curve fit equation, one can convert this back into a voltage value with the following equation

$$ V(r, \beta) = \frac{5}{\frac{R(r,\beta)}{330} + 1}  $$

The voltage value and the resistance value are inversely proportional, i.e. as the photoresistor's resistance grows, the measured voltage drop in the circuit shrinks. The maximum resistance $R_{max} = 337260$ corresponds to a minimum voltage drop $V_{min} \approx 0.004$ and the minimum resistance $R_{min} = 100$ corresponds to a maximum voltage drop $V_{max} \approx 4$.

## Matlab Plotting Script
Within this directory, there is also a [matlab plotting script](/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/photoresistor_measurement_3Dplots.m) which is responsible for creating nice 3D plots to visualize the cost function created in the python script. The standard quadratic curve fits are visualized below.

![3D resistance contours](/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/figures/resistance_contours_3D.png)

![3D voltage contours](/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/figures/voltage_contours_3D.png)

If a user wants to mimic the readings one would get from the Arduino with an analog to digital converter, they would be utilizing the cost functions seen below.

![3D ADC resistance contours](/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/figures/resistance_contours_3D_with_ADC.png)

![3D ADC voltage contours](/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/figures/voltage_contours_3D_with_ADC.png)
