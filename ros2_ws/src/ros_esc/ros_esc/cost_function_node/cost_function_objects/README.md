# Description:

This folder contains examples of cost function and noise objects for use in experimental
testing. These scripts are referenced by the cost function configuration json file. To
use a cost function or noise object in an experiment the user must simply name the desired
cost function and noise object within the config file and give it some parameters to initialize
the objects. This node will parse the configuration file, instantiate the cost function and
noise objects, and then use the cost output method to operate on input values, and the add
noise method to add noise to the cost value signal.
