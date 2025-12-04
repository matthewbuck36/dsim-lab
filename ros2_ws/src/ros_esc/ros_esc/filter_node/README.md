# Node Description:

The purpose of this node is to create a filter node which allows custom filters to be used with ROS2 communication. The user will pass in a custom filter configuration that is either written out in a json file, or passed in as a string. This code will construct that configuration, making use of filters and parameter ODEs built in the extremum seeking package. 

## ROS Communication:

Input Topic Subscriptions:

- Input Value Topic: Used to collect StampedFloat64MultiArray messages which contain input values for the filter to operate on.

- Input Encoder Topic: Used to collect StampedFloat64MultiArray messages which contain encoder values to reference. The user has
the option to concatenate these encoder values with input values which will be inputted into the together.

- Input Timekeeper Topic: Used to collect Timekeeper messages which contain timekeeping information to reference.

Output Topic Publishing:

- Output Topic: The node publishes StampedFloat64MultiArray messages containing filter output values.

## Custom Filter Description:

The filter node is responsible for parsing a configuration file, creating the custom filter as described, and using it with ROS2 communication to operate on input values. Each filter in the configuration file (with the exception of Cascade and Parallel filters) must be written as a dictionary. The elements contained within the dictionary, called keys, can contain things like gains, filter dimensions, functions, symbols etc. Each key must have a string as a name to indicate what the following value means. Typically these names come from the required inputs for that particular filter in the extremum-seeking package, however more complicated filters like the ConvolutionFilter, FunctionFilter, and DirectionalFilter, require additional keys to fully describe and initialize the filter. Note for single input, single output (SISO) filters, the dictionary keys would refer to values of type int or float. However, for multi input multi output (MIMO) systems, the dictionary keys may refer to lists of ints or floats, which may correspond to multiple gains.

Cascade and Parallel filters are aggregate filters, meaning they are built up one or more subfilters. When describing these filters in a configuration file, note they are written as a list of dictionaries separated by commas i.e. [dict_1, dict_2, ...]. Think of this as a  list of several sub filters, which will be combined together in an aggregate filter.  Cascade filters combine all the sub filters in series in the order they appear in the file.  Parallel filters combine all sub filters in parallel. There is no limit to the amount of sub  filters contained in these aggregate filters.

Some filters, like Convolution and Function filters may contain user defined functions to operate with. In this case, several keys are required for the filter node to correctly create the filter object. A "function" key is required for the user to define their custom function for the filter to use, this function must be written as a string. A "symbols" key may be used to define the base symbol the function uses. For a function defined as f(t), this base symbol would be "t", however for a function defined f(y), the symbol would be defined as "y". Note if a symbols key is used in a function filter, the equation will be parsed with sympy parse expression, then converted to a lambda function using sympy lambdify. However if a function is defined with no symbols key, the expression will be parsed with the eval() function. There are subtle differences in parsing functions between these two methods that are not covered here. Finally, an optional "substitutions" key is used to define additional symbols and expressions that are substituted into the main function, all of these written out in another dictionary. This key allows for the user to build up complex functions from smaller expressions. One must note however that any additional variables introduced in the substitutions dictionary must either be constants, or somehow dependent on the base variable defined by "symbols". 

To use functions in the MIMO case, these "function", "symbols", and "substitutions" keys must now refer to lists where the indices correlate with one another. In this case, "function" refers to a list of strings representing expressions, "symbols" refers to a list of strings representing the base symbol for each expression, and "substitutions" refers to a list of dictionaries, where each dictionary contains the substitutions for one expression. See EXAMPLE 3 for more details.

## Custom Filter Examples:

The following presents some examples of custom filters along with brief explanations describing their architecture. More examples of filter configuration files can be found in the [filter files](/ros_esc/filter_node/filter_files) directory.

### Example 1:
![Example 1 picture](/ros_esc/filter_node/example_1.png)
```
{
    "CascadeFilter":[
        {
            "LowPassFilter":{"omega_l": 1.0, "init_states": [1.0]}
        },
        {
            "HighPassFilter":{"omega_h": 0.5}
        }
    ]
}
```

This example uses a CascadeFilter to put a list of two subfilters, LowPassFilter and HighPassFilter, into a series connection. Both of these subfilters are SISO, with gains specified in their respective dictionaries. The CascadeFilter puts the subfilters in the serial connection in the order they appear, i.e. the input to the custom filter passes through the LPF first, then the HPF. Note that the LowPassFilter is given an initial state array to use, while the HighPassFilter is not. Any filter with internal dimensions that is not given any initial states will be initialized with an appropriate amount of zeros, however this can be overriden with custom initial states using the "init_states" key as seen here. Once this filter is parsed, the vector of the custom filter initial states will be [1, 0].

### Example 2:
![Example 2 picture](/ros_esc/filter_node/example_2.png)
```
{
    "ParallelFilter":[
        {
            "CascadeFilter":[
                {
                    "FunctionFilter":
                    {
                        "function": "2*a*u",
                        "symbols": "u",
                        "substitutions": {"a": 4},
                        "idim": 1,
                        "odim": 1
                    }
                },
                {
                    "FunctionFilter":
                    {
                        "function": "u/3",
                        "symbols": "u",
                        "idim": 1,
                        "odim": 1
                    }
                }
            ]
        },
        {
            "FunctionFilter":
            {
                "function": "1/2*(c-d)",
                "symbols": "u",
                "substitutions": {"c": 4, "d": "1/2*u"},
                "idim": 1,
                "odim": 1
            }
        }
    ]
}
```

This example puts uses a ParallelFilter to put a list of two subfilters, CascadeFilter and FunctionFilter, into a parallel connection, meaning they both receive the same input. Note the use of the "function", "symbols", and "substitutions" keys in the function filters. Each expression in "function" is written as a string. Each symbol in "symbols" is a string representing the base variable (u in this case). Finally note that some filters make use of the "substitutions" key, while others do not. Note in the bottom FunctionFilter, the base symbol "u" does not appear directly in the "function" expression, rather it comes up through the substitutions. Note that this base symbol could be any string, meaning these filters could have been written with base symbols "y", "phi", "theta" etc. Substitutions may be used to sub in constants, or used to sub in additional expressions written as strings.

### Example 3:
![Example 3 picture](/ros_esc/filter_node/example_3.png)
```
{
    "CascadeFilter":[
        {
            "WashoutFilter":{
                "omega": 1.0
            }
        },
        {
            "ConvolutionFilter":{
                "function": ["2/d*cos(phi)","2/d*sin(phi)"],
                "symbols": ["t","t"],
                "substitutions": [
                    {"d": 0.1524, "phi": "phi0 + omega*t", "phi0": 0, "omega": "2*pi/60*rpm", "rpm": 20},
                    {"d": 0.1524, "phi": "phi0 + omega*t", "phi0": 0, "omega": "2*pi/60*rpm", "rpm": 20}
                ],
                "odim": 2
            }
        },
        {
            "DirectionalFilter":{
                "param_ode": "RMSpropFlow",
                "k": [0.1,0.1],
                "omega_l": 1.0
            }
        }
    ]
}
```

In this example, the CascadeFilter is used to put a WashoutFilter, a ConvolutionFilter, and a DirectionalFilter into a series connection. In the ConvolutionFilter, we again see the "function", "symbols", and "substitutions" keys appear, however now they are used in the MIMO case. Each of these keys refer to lists where the indicies correlate with one another. Note that a ConvolutionFilter must have the base symbol "t", this is required unlike the FunctionFilter. Additionally, note in these substitutions dictionaries, the substitutions can be written out in any order. As long as everything is accounted for, the filter node will parse it down to a final expression. In the DirectionalFilter, a "param_ode" is specified. This refers to a parameter update ODE found in the extremum-seeking package. The additional keys: "k" and "omega_l" are used to initialize the parameter update ODE object. Note in this case, "k" is a list so this DirectionalFilter is MIMO.

### Example 4:
![Example 4 picture](/ros_esc/filter_node/example_4.png)
```
{
    "CascadeFilter":[
        {
            "ParallelFilter":[
                {
                    "CascadeFilter":[
                        {
                            "FunctionFilter":{
                                "function": "u[0]",
                                "idim": 1,
                                "odim": 1
                            }
                        },
                        {
                            "FunctionFilter":{
                                "function": "theta + c1",
                                "symbols": ["theta"],
                                "substitutions": [
                                    {
                                        "c1": "pi/2"
                                    }
                                ],
                                "idim": 1,
                                "odim": 1
                            }
                        }
                    ]
                },
                {
                    "CascadeFilter":[
                        {
                            "FunctionFilter":{
                                "function": "u[1]",
                                "idim": 1,
                                "odim": 1
                            }
                        },
                        {
                            "FunctionFilter":{
                                "function": [
                                    "c2 * cos(phi)",
                                    "c3 * sin(phi)"
                                ],
                                "symbols": ["phi","phi"],
                                "substitutions": [
                                    {
                                        "c2": "pi/4"
                                    },
                                    {
                                        "c3": "pi"
                                    }
                                ],
                                "idim": 1,
                                "odim": 2
                            }
                        }
                    ]
                }
            ]
        },
        {
            "FunctionFilter":{
                "function": [
                    "u[0]*u[1]",
                    "u[0]*u[2]"
                ],
                "idim": 3,
                "odim": 2
            }
        }
    ]
}
```

The user may run into a case where they need to demux and mux signals in their custom filter. This is accomplished by clever use of ParallelFilters and FunctionFilters. In this example, the input to this filter is assumed to be an array with two elements given by

$$ Custom Filter Input = [\theta , \phi] $$

The ParallelFilter along with the first FunctionFilter on each parallel track are used to demux the input signal. The function $u[0]$ will simply return the first entry of the custom filter input, $\theta$, similarly $u[1]$ will return $\phi$. Now we have one track of the ParallelFilter where each subsequent filter in series will operate on the value $\theta$ and another track where the same happens for $\phi$. We use more FunctionFilters to perform some mathematical operations on these values.

When we want to mux these signals back together, we use another FunctionFilter immediately following the end of the ParallelFilter configuration. In this example, this "muxing" FunctionFilter takes in three inputs, one coming from the $\theta$ track, and the other two coming from the $\phi$ track of the of the ParallelFilter. The following equation multiplies the result from the $\theta$ track by each result of the $\phi$ track. This example demonstrates how one can construct mathematical equations using this demuxing and muxing technique with filter blocks.

$$ Custom Filter Output = [(\theta + pi/2) * (pi/4*cos(\phi)) , (\theta + pi/2) * (pi*sin(\phi))] $$

This example is useful because this demuxing and muxing technique is used when working with estimation signals for ESC control. Normally, one would convolve with time varying estimation signals like the ones shown in the ConvolutionFilter in Example 3. Note that these estimation signals are functions of the perturbation signal $\phi(t)$. This perturbation signal physically represents the angular position of the rotating sensor frame on the vehicle. Estimating this $\phi(t)$ signal by explicitly writing it out as a function of time works fine for simple math simulations. However when working with Gazebo or real life vehicles, estimating $\phi(t)$ with the ConvolutionFilter introduces timing issues since the actual angular position may differ from the estimated $\phi(t)$. This the error will build up as time goes on and make the ESC controller useless.

It is much better to "convolve" with the actual angular position rather than an estimate by using this demuxing and muxing technique demonstrated in Example 4. The --encoder_data option for this filter node allows the user to concatenate the angular position readings from the encoder node with the normal inputs to the filter coming from the input topic. For one sensor and one rotating frame, the custom filter input may look something like the following

$$ Custom Filter Input = [J , \phi] $$

The demuxing technique should be used to isolate the cost value J on one track of the parallel filter, while the other track operates on the isolated $\phi$ signal. This way, any filtering or operations that need to be applied to these specific singals can be kept separate. For example, the mathematical operations that are used to generate the estimation signals all happen on the $\phi$ track, and dont affect anything happening to the cost value on the J track. Finally, to "convolve" the estimation signals with the result on the J track, one can mux these two signals together with a FunctionFilter as shown in this example above. 

## Launch Command For This Node:

The following terminal command launches this node. This can be put into a launch file to automatically run this node in an experiment.

```
ros2 run ros_esc filter_node {input_value_topic} {input encoder_topic} {input_timekeeper_topic} {output_topic} --filter_file {input_json_filepath} --encoder_data {'True' or 'False'}
```
