#!/usr/bin/env python3

"""This script holds all the configuration parsing functions needed for the ROS
nodes to operate. The nodes are responsible for parsing config json files and
converting them to object so that they can be used in experiments.
"""

# pylint: disable=wildcard-import
import os
import importlib.util
import numpy as np
import extremum_seeking as es
from extremum_seeking.filters import * # pylint: disable=unused-wildcard-import
from extremum_seeking.seekers import * # pylint: disable=unused-wildcard-import
from sympy.parsing.sympy_parser import parse_expr
from sympy.utilities.lambdify import lambdify
from ros_esc.rotate_frame_node.spin_profile_objects import * # pylint: disable=unused-wildcard-import
from ros_esc.sensor_pose_node.transform_objects import * # pylint: disable=unused-wildcard-import
from ros_esc.cost_function_node.cost_function_objects import * # pylint: disable=unused-wildcard-import
from ros_esc.controller_node.controller_objects import * # pylint: disable=unused-wildcard-import

# The following methods are used to parse objects defined within config files:

def parse_object_config(config_dict):
    """This is used by to parse an object specified in a configuration file.

    This function makes use of the importlib library to import a python
    script as a module in the middle of the code's execution. The desired
    object from that python module is collected. The object is intitialized
    with additional dictionaries specified in the config and then returned.

    Reference:
    https://www.geeksforgeeks.org/how-to-import-a-python-module-given-the-full-path/
    """

    # Get the filepath to the desired object's script
    filepath_str = config_dict["filepath"]
    # Get the script name from the filepath
    script_name = filepath_str.split("/")[-1]
    # Remove the tag at the end of the script name
    script_name = script_name.split(".")[0]
    # Get the name of the object to look for in that file
    object_name = config_dict["object_name"]
    # Redefine the filepath to accomodate the user's home directory
    filepath = os.path.expanduser(config_dict["filepath"])

    # Specify the module that needs to be imported
    spec = importlib.util.spec_from_file_location(script_name, filepath)
    # Creates a new module based on spec
    module = importlib.util.module_from_spec(spec)
    # Executes the module in its own namespace when a module is imported or reloaded
    spec.loader.exec_module(module)
    # Check if this is an object that exists in that script
    warn_msg = '\n'.join([
        "Object '"+str(object_name),
        "' does not exist in script at "+str(filepath_str)
    ])
    assert hasattr(module, object_name), warn_msg
    # Get the correct object class from the module
    object_class = getattr(module, object_name)

    # Delete the path and object name keys from the dict
    del config_dict["filepath"]
    del config_dict["object_name"]

    # Instantiate the object with the keys from the dictionary
    instantiated_obj = object_class(**config_dict)

    return instantiated_obj

def parse_object_into_str(config_dict):
    """This function returns the object code as a string.

    Note that the "return output" string of text denotes the end of the code
    for a particular object. This method will parse the object as a string from
    "class {object_name}" to the end specified by "return output".

    This method is used by the data collection node to document the
    object used in an experiment for future reference. This function
    will read the file at the specified filepath. It searches for the
    specified object, then returns the object code as a string.
    """

    # Get the filepath to the object's script
    filepath_str = config_dict["filepath"]
    # Get the script name from the filepath
    script_name = filepath_str.split("/")[-1]
    # Remove the tag at the end of the script name
    script_name = script_name.split(".")[0]
    # Get the name of the object to look for in that file
    object_name = config_dict["object_name"]
    # Redefine the filepath to accomodate the user's home directory
    filepath = os.path.expanduser(config_dict["filepath"])

    # Open the script at the filepath
    with open(filepath, mode='r', encoding='utf-8') as file:
        # Read the file
        file_text = file.read()
        # Split the string of text up by defined classes
        split_text = file_text.split("class "+object_name)
        # Keep everything after the split
        text = split_text[1]
        # Split the string of text up by the object ending indicator text
        # which denotes the end of the code for each object
        text = text.split("return output")
        # Keep everything before the first split,
        # this is the code describing the object
        obj_code = text[0] + "return output"
        # Collect the object written as a string
        object_str = "class "+object_name+obj_code

    return object_str

# The following methods are used to parse config files for specific nodes:

# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
def parse_filter_config(config_dict, filter_state_vector):
    """This is used by the filter node to parse a configuration file.

    This parses an input custom filter config dictionary coming from a json file.
    Inside this dictionary, the custom filter's architecture is specified.
    This function will parse and return the custom filter using filter objects from the
    extremum seeking package.
    """

    # Initialize the custom filter
    custom_filter = None

    # Iterate through each entry
    # pylint: disable=too-many-nested-blocks
    for entry_name in config_dict:

        # Check if this is a filter that exists in the extremum seeking package
        # If the filter doesn't exist, raise an exception
        warn_msg = "Filter '"+str(entry_name)+"' does not exist in package: extremum seeking."
        assert hasattr(es.filters, entry_name), warn_msg

        # Ensure this is not the "Filter" obejct from the package
        warn_msg = "You selected the class '"+str(entry_name)+"' which cannot be used as a filter."
        assert (entry_name[-6:] == "Filter" and len(entry_name) > 6), warn_msg

        # Check if this is a cascade or parallel filter
        if entry_name in ("CascadeFilter", "ParallelFilter"):
            # Extract the list of subfilters
            subfilter_list = config_dict[entry_name]

            # Create a list to hold instantiated filters
            instantiated_subfilters = []

            # Parse through all of the sub filters in the list
            # by recursively calling this function
            for entry in subfilter_list:
                # Recursively parse the filter
                subfilter, filter_state_vector = parse_filter_config(entry, filter_state_vector)
                # Append the filter to the list
                instantiated_subfilters.append(subfilter)

            # subfilter_list = [parse_filter_config(x, filter_state_vector) for x in subfilter_list]

            # Create the combined filter
            # Note the * character unpacks the subfilter list
            # which allows us to pass it as an input argument
            if entry_name == "CascadeFilter":
                custom_filter = CascadeFilter(*instantiated_subfilters)
            elif entry_name == "ParallelFilter":
                custom_filter = ParallelFilter(*instantiated_subfilters)

        # Otherwise we parse a regular filter
        else:
            # Get the correct filter class from the extremum seeking package
            filter_class = getattr(es.filters, entry_name)
            # Collect the dictionary of information describing this filter
            filter_config = config_dict[entry_name]

            # Check if there is a user defined function within this dictionary
            if "function" in filter_config:
                # Assert that there are no initial conditions specified for this filter
                if "init_states" in filter_config:
                    warn_msg = "\n".join([
                        "Filter "+str(filter_config)+" cannot ",
                        "be created with initial conditions."
                    ])
                    raise Exception(warn_msg)
                # Parse the function in the dictionary
                if "symbols" in filter_config:
                    # Perform checks on the input dictionary
                    # Assert that the function and symbols keys are the same type
                    warn_msg = '\n'.join([
                        "Function and symbols are of incompatible types ",
                        "in "+str(filter_config)+" filter."
                    ])
                    assert isinstance(
                        filter_config["function"],
                        type(filter_config["symbols"])
                    ), warn_msg

                    # If there is a substitutions key
                    if "substitutions" in filter_config:
                        # Assert substitutions is either a dict or a list
                        if isinstance(filter_config["function"], str):
                            warn_msg = '\n'.join([
                                "Substitutions is an incompatible type ",
                                "in "+str(filter_config)+" filter.",
                                "If function is defined as a string, ",
                                "substitutions must be defined as a dict."
                            ])
                            assert isinstance(filter_config["substitutions"], dict), warn_msg
                        elif isinstance(filter_config["function"], list):
                            warn_msg = '\n'.join([
                                "Substitutions is an incompatible type ",
                                "in "+str(filter_config)+" filter.",
                                "If function is defined as a list, ",
                                "substitutions must be defined as a list."
                            ])
                            assert isinstance(filter_config["substitutions"], list), warn_msg

                    # If there are symbols, create a lambda function with sympy
                    # pylint: disable=unused-variable
                    filter_function, filter_expression = parse_sympy_expression(filter_config)
                else:
                    # If there are no symbols, create a lambda function with eval
                    filter_function = parse_function_string(filter_config)

                # After parsing the function, delete unnecessary keys from the dictionary
                del filter_config["function"]
                if "symbols" in filter_config:
                    del filter_config["symbols"]
                if "substitutions" in filter_config:
                    del filter_config["substitutions"]

                # Add in a key with the new function
                filter_config["f"] = filter_function

            # Check if there is a parameter ode within this dictionary
            if "param_ode" in filter_config:
                # Parse that parameter ode
                filter_config = parse_ode(filter_config)

            # Loop through the filter dictionary,
            # convert any lists to numpy arrays
            for key in filter_config:
                if isinstance(filter_config[key], list):
                    filter_config[key] = np.array(filter_config[key])

            # Check for initial states defined in the config
            init_state_array = None
            if "init_states" in filter_config:
                # Get the initial states to add
                init_state_array = filter_config["init_states"]
                # Delete the initial state key
                del filter_config["init_states"]

            # Create an instance of this class with our input parameters
            # We unpack the filter dictionary with the ** operator
            # Since every item has a key in the filter dictionary
            # we don't need to worry about putting things in the correct order
            custom_filter = filter_class(**filter_config)

            # If there are were initial states given for this filter, initialize with zeros
            if init_state_array is None:
                # Check the dimensions of the custom filter
                size = custom_filter.ndim
                # Create an array of zeros based on the size
                init_state_array = np.zeros((size))

            # If there were initial states given for this filter
            else:
                # Assert that the number of initial states
                # given matches the ndim of the initialized filter
                warn_msg = "\n".join([
                    "Number of initialized states ("+str(len(init_state_array))+") in ",
                    "filter ("+entry_name+") does not match the number of internal ",
                    "dimensions, ndim ("+str(custom_filter.ndim)+")"
                ])
                assert custom_filter.ndim == len(init_state_array), warn_msg

            # Concatenate the initial states to the custom filter state vector
            filter_state_vector = np.concatenate((filter_state_vector, init_state_array), axis=0)

    # Return custom filter
    return custom_filter, filter_state_vector

def parse_optimal_position_expression(config_dict, variable, timestamps):
    """This function returns information about the optimal or source's, position.

    Every cost function config file should come with keys in the params dictionary
    which describe the (x, y, z), possibly time varying, position of the optimal
    point. These descriptions will be parsed into sympy expressions. If the position
    of the optimal point varies with time, this sympy expression will be evaluated
    with input timestamps to calculate the trajectory of the point.
    """

    # Get the optimal position description
    if variable in config_dict:
        # Get the expression
        description = config_dict[variable]
        # Delete this key from the dict and use the rest as possible subsitutions
        del config_dict[variable]
    else:
        description = 0

    # If this description is a float or int, do not parse with sympy
    # pylint: disable=no-else-return
    if isinstance(description, (float, int)):
        # Set the initial position
        init_pos = description
        # Set the trajectory list
        trajectory = None
        # Return results
        return init_pos, trajectory

    # If this description is a string representing some expression
    elif isinstance(description, str):
        # Define the symbols list, all expressions must only be a function of time
        symbols_list = ['t']
        # Use the remaining keys in the config dict as possible substitutions
        subs_dict = config_dict
        # Create an expression with sympy
        funct, _ = create_function(description, symbols_list, subs_dict)

        # Initialize the trajectory list
        trajectory = []
        # Evaluate the function with the given timestamps
        for time in timestamps:
            # Input the time
            trajectory.append(funct(time))
        # Get the initial position
        init_pos = trajectory[0]

        # Return results
        return init_pos, trajectory


    # If this description is none of the above, raise an error
    else:
        warn_msg = "\n".join([
            "Optimal position message with variable "+str(variable)+" is ",
            "not of type int, float, or string. Please convert this to ",
            "a parseable expression."
        ])
        raise Exception(warn_msg)

# The following methods are used to parse functions defined within config files:

def parse_sympy_expression(config_dict):
    """This parses a user defined function within the dictionary.

    To parse this function, the 'function' and 'symbols' keys are required in the
    filter dictionary. An optional key 'substitutions' is used to perform any variable
    substitutions into the origional function for long mathematical equations. This
    function will create a lambda function and return it.
    """

    # Initialize variables
    funct = config_dict["function"]
    symb = config_dict["symbols"]

    # Initialize substitutions if we have them
    if "substitutions" in config_dict:
        subst = config_dict["substitutions"]
    else:
        subst = None

    # If we're dealing with lists of functions
    if isinstance(funct,list):
        # Assert that the function and symbols lists are the same size
        warn_msg = '\n'.join([
            "Function list and symbols list are not ",
            "the same size in "+str(config_dict)+" config."
        ])
        assert len(funct) == len(symb), warn_msg
        # Assert that substitutions list is the same size if it exists
        if subst is not None:
            warn_msg = '\n'.join([
                "Substitutions list is not the same ",
                "size as function & symbols list ",
                "in "+str(config_dict)+" config."
            ])
            assert len(subst) == len(funct), warn_msg

        # Initialize a list to store individual lambda functions
        f_list = []
        sympy_expressions = []
        # Loop through each entry in the list of functions
        for entry in enumerate(funct):
            # Get the index
            index = entry[0]
            # Create the lambda function and expression
            lam_funct, sp_expr = create_function(funct[index], symb[index], subst[index])
            # Append the lambda function to the function list
            f_list.append(lam_funct)
            # Append the sympy expression to the expression list
            sympy_expressions.append(sp_expr)

        # Go from list of scalar functions to a multivariable output function.
        lambda_functions = lambda x: np.array([fi(x) for fi in f_list])

    # If we're not dealing with lists
    else:
        lambda_functions, sympy_expressions = create_function(funct, symb, subst)

    return lambda_functions, sympy_expressions

def create_function(func_str, symbol_list, subs_dict):
    """This method uses sympy to create a lambda function.

    This method returns the sympy expression with the substitutions
    worked out and the lambda function for that expression.
    """

    # Create sympy expression
    expression = parse_expr(func_str)

    # Check if there is a dictionary of substitutions to be parsed
    if subs_dict is not None:
        # subs_dict will be formatted as a dictionary:
        # {"variable" : expression for the variable, ...}

        # Note this dictionary of substitutions can be written out randomly,
        # this code ensures that we make those substitutions into the main
        # expression in the correct order
        expression = parse_subs(expression, symbol_list, subs_dict)

    # Use sympy to convert this expression into a lambda function
    funct = lambdify(symbol_list, expression, 'numpy')

    return funct, expression

def parse_subs(expression, symbol_list, subs_dict):
    """This method parses substitutions into an expression.

    This function utilizes the free symbols attribute of sympy's
    expression object to parse substitutions from the substitutions
    dictionary into the main expression.
    """

    # Get the free symbols from our expression
    free_symb = expression.free_symbols
    # Loop through the free symbols
    for symb in enumerate(free_symb):
        # Get the symbol
        symb = str(symb[1])
        # If this free symbol is a base symbol from symbol_str, do nothing
        if symb in symbol_list:
            continue

        # Check if this symbol appears anywhere in our substitution dictionary
        if symb in subs_dict:
            # Get the sub expression related to this symbol
            sub_expr = subs_dict[symb]
            # Check if the entry at the symb key is a string representing another expression
            if isinstance(sub_expr, str):
                # Parse the subexpression with sympy
                sub_expr = parse_expr(sub_expr)
                # Get the free symbols for the sub expression
                sub_free_symb = sub_expr.free_symbols
                # Check if this entry is itself another expression that needs substitution
                # If not all of the symbols in the substitution can be accounted for in
                # the list of base symbols
                if not all(symb in sub_free_symb for symb in symbol_list):
                    # Recursively call this function to do another substitution
                    sub_expr = parse_subs(sub_expr, symbol_list, subs_dict)
                # Do the substitution into expression
                expression = expression.subs(symb,sub_expr)

            # Otherwise just substitute
            else:
                expression = expression.subs(symb,sub_expr)

        # If this symbol doesn't appear anywhere, raise exception
        else:
            warn_msg = "Symbol "+str(symb)+" is not found in lists symbols or substitutions."
            raise Exception(warn_msg)

    return expression

def parse_ode(filter_config):
    """This creates a parameter ODE object to be used in the directional filter.

    This function takes a filter configuration dictionary as an input. This function
    then instantiates a parameter update ODE from the extremum seeking class based
    on the configuration described in the filter config dictionary. This function
    then remakes the filter configuration dictionary so that the only key 'g' refers
    to this instantiated update ODE object. This remade filter config dictionary is
    then returned.
    """

    # Get the ODE name
    ode_name = filter_config["param_ode"]
    # Delete the param_ode key
    del filter_config["param_ode"]

    # Check if this is a parameter update ODE that exists in the extremum seeking package
    # If the ODE doesn't exist, raise an exception
    if not hasattr(es.seekers,ode_name):
        warn_msg = '\n'.join(
            "Parameter update ODE '"+str(ode_name)+
            "' does not exist in package: extremum seeking."
        )
        raise Exception(warn_msg)

    # Check if this is a parameter update ODE that we can actually use
    # If this is a class in extremum_seeking/seekers that we shouldn't use, raise an exception
    if not (ode_name[-4:] == "Flow" and len(ode_name) > 4):
        warn_msg = '\n'.join(
            "You selected the class '"+str(ode_name)+
            "' which cannot be used as a parameter update ODE."
        )
        raise Exception(warn_msg)

    # If we pass these checks we get the correct param ODE class from extremum_seeking/seekers
    ode_class = getattr(es.seekers,ode_name)

    # Loop through the filter dictionary, convert any lists to numpy arrays
    for key in filter_config:
        if isinstance(filter_config[key], list):
            filter_config[key] = np.array(filter_config[key])

    # Check for an initial state key, save the array
    init_state_array = None
    if "init_states" in filter_config:
        # Save the initial state array
        init_state_array = filter_config["init_states"]
        # Delete the initial state key
        del filter_config["init_states"]

    # Create an instance of this class with our input parameters
    # The rest of the keys in the filter dictionary are the input parameters,
    # they all get unpacked with the ** operator
    custom_ode = ode_class(**filter_config)

    # Remake filter to only contain a key for our custom ode, and initial states
    if init_state_array is not None:
        filter_config = {'g': custom_ode, "init_states": init_state_array}
    else:
        filter_config = {'g': custom_ode}

    return filter_config

def parse_function_string(config_dict):
    """This parses a user defined function within the dictionary.

    To parse this function, the 'function' key is required to have strings
    represent some function of a variable u. The variable u represents the function
    input, note no other variable can be used. This function will create a lambda
    function and return it.
    """

    # Initialize variables
    funct = config_dict["function"]

    # If we're dealing with lists of functions
    if isinstance(funct,list):
        # Create a list to hold the results
        f_list = []
        # Loop over all functions in the list
        for entry in enumerate(funct):
            # Get the index
            index = entry[0]
            # Get the function string
            funct_str = funct[index]
            # Append to our list of functions
            f_list.append(parse_str(funct_str))
        # Go from list of scalar functions to a multivariable output function.
        lambda_functions = lambda x: np.array([fi(x) for fi in f_list])
    # Otherwise parse the function string with eval
    else:
        # Parse the function string with eval
        lambda_functions = parse_str(funct)

    return lambda_functions

def parse_str(funct_str):
    """This function parses an input string and creates a lambda function."""

    return lambda u: np.array(eval(funct_str))
