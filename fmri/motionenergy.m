function [total_energy, left_Total, right_Total, motion_energy]=motionenergy(stim)
% based on http://www.georgemather.com/Model.html
[numframes, numpix]=size(stim);
% Step 1a ---------------------------------------------------------------
%Define the space axis of the filters
%nx=80;              %Number of spatial samples in the filter
nx=numpix/2; %since example was 160 units and nx=80; 2 in denominator comes from stim_width(below)/2
max_x =2.0;         %Half-width of filter (deg)
dx = (max_x*2)/nx;  %Spatial sampling interval of filter (deg)
%dx=.01;% 8 degree stimulus, 82 pix in x dimension 8/82~.01

% A row vector holding spatial sampling intervals
x_filt=linspace(-max_x,max_x,nx);
 
% Spatial filter parameters
sx=0.5;   %standard deviation of Gaussian, in deg.
sf=1.1;  %spatial frequency of carrier, in cpd
 
% Spatial filter response
gauss=exp(-x_filt.^2/sx.^2);          %Gaussian envelope
even_x=cos(2*pi*sf*x_filt).*gauss;   %Even Gabor
odd_x=sin(2*pi*sf*x_filt).*gauss;    %Odd Gabor
%--------------------------------------------------------------------
% Step 1b ----------------------------------------------------------------
% Define the time axis of the filters
nt=100;         % Number of temporal samples in the filter
%nt=numframes/2; %since example was 201 frames and nt=100
max_t=0.5;      % Duration of impulse response (sec)
dt=0.0333;%4 second clip-->120 frames; 4/120=0.0333%dt = max_t/nt;  % Temporal sampling interval (sec)
nt=max_t/dt;

% A column vector holding temporal sampling intervals
t_filt=linspace(0,max_t,nt)';
 
% Temporal filter parameters
k = 100; % Scales the response into time units
slow_n = 9; % Width of the slow temporal filter
fast_n = 6; % Width of the fast temporal filter
beta =0.9; % Weighting of the -ve phase of the temporal resp relative to the +ve phase.
 
% Temporal filter response
slow_t=(k*t_filt).^slow_n .* exp(-k*t_filt).*(1/factorial(slow_n)-beta.*((k*t_filt).^2)/factorial(slow_n+2));
 
fast_t=(k*t_filt).^fast_n .* exp(-k*t_filt).*(1/factorial(fast_n)-beta.*((k*t_filt).^2)/factorial(fast_n+2));
%--------------------------------------------------------------------
% Step 1c --------------------------------------------------------
e_slow= slow_t * even_x; %SE/TS
e_fast= fast_t * even_x ; %SE/TF
o_slow = slow_t * odd_x ; %SO/TS
o_fast = fast_t * odd_x ; % SO/TF
%-----------------------------------------------------------------
% Step 2 ---------------------------------------------------------
left_1=o_fast+e_slow; % L1
left_2=-o_slow+e_fast; % L2
right_1=-o_fast+e_slow; % R1
right_2=o_slow+e_fast; % R2
%-----------------------------------------------------------------
% Step 3a ---------------------------------------------------------
% SPACE: x_stim is a row vector to hold sampled x-positions of the space.
stim_width=4;  %half width in degrees, gives 8 degrees total
x_stim=-stim_width:dx:round(stim_width-dx);
 
% TIME: t_stim is a col vector to hold sampled time intervals of the space
stim_dur=4; %1.5;    %total duration of the stimulus in seconds
t_stim=(0:dt:round(stim_dur-dt))';
%--------------------------------------------------------------------
% Step 3b -----------------------------------------------------------
%load 'AB15.mat';% Oscillating edge stimulus. Loaded as variable ?stim?
% OR
%load 'AB16.mat';% RDK stimulus. Loaded as variable ?stim?
%--------------------------------------------------------------------
% Step 3c -----------------------------------------------------------
% Rightward responses
resp_right_1=conv2(stim,right_1,'valid');
resp_right_2=conv2(stim,right_2,'valid');
 
% Leftward responses
resp_left_1=conv2(stim,left_1,'valid');
resp_left_2=conv2(stim,left_2,'valid');
%--------------------------------------------------------------------
% Step 4 -------------------------------------------------------------
resp_left_1 = resp_left_1.^2;
resp_left_2 = resp_left_2.^2;
resp_right_1 = resp_right_1.^2;
resp_right_2 = resp_right_2.^2;
%--------------------------------------------------------------------
% Step 5 ------------------------------------------------------------
% Calc left and right energy
energy_right= resp_right_1 + resp_right_2;
energy_left= resp_left_1 + resp_left_2;
 
% Calc total energy
total_energy = sum(sum(energy_right))+sum(sum(energy_left));
 
% Normalise
RR1 = sum(sum(resp_right_1))/total_energy;
RR2 = sum(sum(resp_right_2))/total_energy;
LR1 = sum(sum(resp_left_1))/total_energy;
LR2 = sum(sum(resp_left_2))/total_energy;
%--------------------------------------------------------------------
% Step 6 -------------------------------------------------------------
right_Total = RR1+RR2;
left_Total = LR1+LR2;
%---------------------------------------------------------------------
% Step 7 -------------------------------------------------------------
motion_energy = right_Total - left_Total;
motion_energy_nodirection=right_Total+left_Total;
fprintf('\n\nNet motion energy = %g\n\n',motion_energy);
%---------------------------------------------------------------------
% Plot model output ---------------------------------------------------
% Generate motion contrast matrix
energy_opponent = energy_right - energy_left; % L-R difference matrix
[xv yv] = size(energy_left); % Get the size of the response matrix
energy_flicker = total_energy/(xv * yv); % A value for average total energy
 
% Re-scale (normalize) each pixel in the L-R matrix using average energy.
motion_contrast = energy_opponent/energy_flicker;
 
% Plot, scaling by max L or R value
mc_max = max(max(motion_contrast));
mc_min = min(min(motion_contrast));
if (abs(mc_max) > abs(mc_min))
    peak = abs(mc_max);
else
    peak = abs(mc_min);
end
total_energy=total_energy/100000000000; 
%figure
%imagesc(motion_contrast);
%colormap(gray);
%axis off
%caxis([-peak peak]);
%axis equal
%title('Normalised Motion Energy');
%--------------------------------------------------------------------