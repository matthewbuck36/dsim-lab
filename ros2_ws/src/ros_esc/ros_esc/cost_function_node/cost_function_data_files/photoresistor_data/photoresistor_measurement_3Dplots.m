%% Documentation
% This matlab script is used to visualize the virtual light source cost
% function as 3D plots. This script makes several figures which show the
% cost function in different perspectives.

%% Data Collection

clc;

% Collect the csv data
data = csvread("curve_fitting_data.csv", 1, 0);
% Separate the columns into data variables
fit_radius = data(:,1);
fit_angle = data(:,2);
fit_ohms = data(:,3);
fit_voltage = data(:,4);

% Define the minimum and maximum resistance (in ohms)
min_resistance = 100;
max_resistance = 337260;

% Collect the colorbar information from the csv file
cbar_data = csvread("plasma_r_colorbar.csv");
cbar_data = [cbar_data(:,1), cbar_data(:,2), cbar_data(:,3)];

%% Plot Curve Fit Data
% This plots the data taken from the csv file and used to make the
% quadratic curve fit.

% Plot the resistance data we want to fit
fig = figure();
scatter3(fit_radius, fit_angle, fit_ohms, 'filled');
set(gca,'FontSize',20, 'FontName', 'TimesNewRoman');
view([-45, 25]);
title("Data Used For Quadratic Curve Fit");
xlabel("$r_s$ [m]",'Interpreter','latex');
ylabel("\beta [deg]");
xlim([0, 6]);
ylim([0, 180]);
zlim([0, 350000]);
xticks([0, 2, 4, 6]);
yticks([0, 45, 90, 135, 180]);
zticks([0, 100000, 200000, 300000]);
zlabel("$R_{\mathrm{pr}}$ [$\Omega$]",'Interpreter','latex');

%% Quadratic Curve Fit Results
% The quadratic curve fit is of the form below:
% resistance(radius, beta) = a*radius^2 + b*beta^2 + c*radius*beta + d*radius + e*beta + f

% This section initializes these values with the results we got from our
% quadratic curve fit.
a = 8.28082113e3;
b = 7.90425287;
c = 4.42130406e2;
d = 5.36416164e-13;
e = 1.68542637e-16;
f = 2.18515692e-18;

%% Plot Quadratic Cost Function
% This plots the quadratic curve fit used as the virtual cost function.

% Initialize radii and beta angles to plot over
radius_range = 0:0.125:6;
beta_range = 0:5:180;
[X, Y] = meshgrid(radius_range, beta_range);

% Initialize a resistance grid
resistance_grid = zeros(length(beta_range), length(radius_range));
% Initialize a voltage grid
voltage_grid = zeros(length(beta_range), length(radius_range));

% Loop over all radii
for i=1:1:length(radius_range)
    % Get the radius at this index
    rad_val = radius_range(i);

    % Loop over all beta angles
    for j=1:1:length(beta_range)
        % Get the beta angle at this index
        beta_val = beta_range(j);

        % Use the curve fit to calculate resistance
        res_val = a*rad_val^2 + b*beta_val^2 + c*rad_val*beta_val + d*rad_val + e*beta_val + f;

        % Ensure this doesn't exceed the largest resistance value
        if res_val > max_resistance
            res_val = max_resistance;
        elseif res_val < min_resistance
            res_val = min_resistance;
        end

        % Save this result to the grid
        resistance_grid(j, i) = res_val;
        % Convert resistance to voltage
        voltage = 5 / (res_val / 330 + 1);
        % Save this result to the grid
        voltage_grid(j, i) = voltage;
    end
end

% Plot the data for the cost function
fig = figure();
surf(X, Y, resistance_grid);
set(gca,'FontSize',20, 'FontName', 'TimesNewRoman');
% Specify colorbar properties
colormap(cbar_data);
% Set the figure view
view([-45, 25]);
% title("Virtual Light Source Resistance Cost Function");
xlabel("$r_s$ [m]",'Interpreter','latex');
ylabel("\beta [deg]");
xlim([0, 6]);
ylim([0, 180]);
zlim([0, 350000]);
xticks([0, 2, 4, 6]);
yticks([0, 45, 90, 135, 180]);
zticks([0, 100000, 200000, 300000]);
zlabel("$R_{\mathrm{pr}}$ [$\Omega$]",'Interpreter','latex');
exportgraphics(fig, "resistance_contours_3D.png", 'Resolution', 300);


% Plot the data for the cost function
% if the resistance is converted to voltage
fig = figure();
surf(X, Y, voltage_grid);
set(gca,'FontSize',20, 'FontName', 'TimesNewRoman');
% Specify colorbar properties
colormap(cbar_data);
% Set colorbar to log scale
set(gca,'ColorScale','log');
% Set the figure view
view([135, 25]);
% title("Virtual Light Source Voltage Cost Function");
xlabel("$r_s$ [m]",'Interpreter','latex');
ylabel("\beta [deg]");
xlim([0, 6]);
ylim([0, 180]);
zlim([0, 5]);
zscale('log');
xticks([0, 2, 4, 6]);
yticks([0, 45, 90, 135, 180]);
zticks([0, 0.005, 0.05, 0.5, 5]);
zlabel("$V_{\mathrm{meas}}$ [V]",'Interpreter','latex');
exportgraphics(fig, "voltage_contours_3D.png", 'Resolution', 300);

%% Arduino ADC Conversion
% This section creates a distinct list of resistance levels to mimic what
% one would get from the Arduino's ADC conversion

% Initialize a list to hold distinct resistance levels
distinct_resistance_list = [];
% Calculate the resistance of the two resistors we have wired in series
% with the photoresistor
series_res = 337260/(5/0.0049 - 1); % result is in ohms


% Calculate the distinct resistance levels
for i=1:1:1024
    distinct_resistance_list(i) = series_res*(5/(i*0.0049) - 1);
end

%% Plot ADC Converted Cost Function
% This plots the virtual light source cost function if we applied the ADC
% conversion to it

% Initialize radii and beta angles to plot over
radius_range = 0:0.125:6;
beta_range = 0:5:180;
[X, Y] = meshgrid(radius_range, beta_range);

% Initialize a resistance grid
resistance_grid = zeros(length(beta_range), length(radius_range));
% Initialize a voltage grid
voltage_grid = zeros(length(beta_range), length(radius_range));

% Loop over all radii
for i=1:1:length(radius_range)
    % Get the radius at this index
    rad_val = radius_range(i);

    % Loop over all beta angles
    for j=1:1:length(beta_range)
        % Get the beta angle at this index
        beta_val = beta_range(j);

        % Use the curve fit to calculate resistance
        res_val = a*rad_val^2 + b*beta_val^2 + c*rad_val*beta_val + d*rad_val + e*beta_val + f;

        % Ensure this doesn't exceed the largest resistance value
        if res_val > max_resistance
            res_val = max_resistance;
        elseif res_val < min_resistance
            res_val = min_resistance;
        end

        % Match this resistance to one of the distinct resistance levels
        res_val = match_reading(distinct_resistance_list, res_val);

        % Save this result to the grid
        resistance_grid(j, i) = res_val;
        % Convert resistance to voltage
        voltage = 5 / (res_val / 330 + 1);
        % Save this result to the grid
        voltage_grid(j, i) = voltage;
    end
end


% Plot the data for the resistance cost function
fig = figure();
surf(X, Y, resistance_grid);
set(gca,'FontSize',20, 'FontName', 'TimesNewRoman');
% Specify colorbar properties
colormap(cbar_data);
% Set the figure view
view([-45, 25]);
% title("Virtual Light Source Resistance Cost Function with ADC Conversion");
xlabel("$r_s$ [m]",'Interpreter','latex');
ylabel("\beta [deg]");
xlim([0, 6]);
ylim([0, 180]);
zlim([0, 350000]);
xticks([0, 2, 4, 6]);
yticks([0, 45, 90, 135, 180]);
zticks([0, 100000, 200000, 300000]);
zlabel("$R_{\mathrm{pr}}$ [$\Omega$]",'Interpreter','latex');
exportgraphics(fig, "resistance_contours_3D_with_ADC.png", 'Resolution', 300);

% Plot the data for the voltage cost function
fig = figure();
surf(X, Y, voltage_grid);
set(gca,'FontSize',20, 'FontName', 'TimesNewRoman');
% Specify colorbar properties
colormap(cbar_data);
% Set colorbar to log scale
set(gca,'ColorScale','log');
% Set the figure view
view([135, 25]);
% title("Virtual Light Source Voltage Cost Function with ADC Conversion");
xlabel("$r_{s}$ [m]",'Interpreter','latex');
ylabel("\beta [deg]");
xlim([0, 6]);
ylim([0, 180]);
zlim([0, 5]);
zscale('log');
xticks([0, 2, 4, 6]);
yticks([0, 45, 90, 135, 180]);
zticks([0, 0.005, 0.05, 0.5, 5]);
zlabel("$V_{\mathrm{meas}}$ [V]",'Interpreter','latex');
exportgraphics(fig, "voltage_contours_3D_with_ADC.png", 'Resolution', 300);

%% Functions Used
function result = match_reading(distinct_list, resistance)
    % This finds the closest possible reading to match the computed resistance value

    % Define a variable to track the error
    error = NaN;
    % Loop over the list of distinct readings
    for i=1:1:length(distinct_list)
        % Calculate the difference
        diff = abs(resistance - distinct_list(i));

        % If this is the first iteration
        if isnan(error)
            % Save the error and move on
            error = diff;
        end

        % Otherwise, if our error increased compared to the previous iteration
        if diff > error
            % Assign the resistance to the previous entry in the list where
            % the error was the smallest
            result = distinct_list(i-1);
            % We can stop iterating at this point
            break;
        end

        % Update our error
        error = diff;
    end
end