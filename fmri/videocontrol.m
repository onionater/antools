function [mov]=videocontrol(directory)

rootdir = '/Users/amyskerry/Documents/Experiments2/aesscripts/EIB_main/'
%rootdir='/Users/amyskerry/Dropbox/antools/fmri/'
stimdir = [rootdir directory];
cd(stimdir)
list= dir('*.mp4');
try
load('stim_control_new.mat')
existingvids=size(mov,2)
catch
existingvids=0    
end
numVids=length(list)
%hbm = vision.BlockMatcher('ReferenceFrameSource','Input port','SearchMethod', 'Three-step');
for v=existingvids+1:numVids
vid=list(v).name;    
readerobj = mmreader(vid);
vidFrames = read(readerobj);
numFrames = get(readerobj, 'numberOfFrames');
m=0;
stdev=0;
rms=0;
cummot=0;
mov(v).name=vid;
mov(v).size=size(vidFrames(:,:,:,1));
videovector=[];
for k = 1 : numFrames
image=vidFrames(:,:,:,k);
im(k).cdata = image; %% color data
im(k).gray = rgb2gray(image); %% grayscale data
imageLum=double(im(k).gray(:));
m=m+mean(imageLum); %% summing up average luminance for each image
stdev=stdev+std(imageLum); %% sum up the variance in luminance for each image
downsampledframe= imresize(im(k).gray, .125);%.25 for faces
imagesize=size(downsampledframe)
numpix=imagesize(1)*imagesize(2);
framevector=reshape(downsampledframe,numpix,1);
videovector=[videovector, framevector];
if k>1
lastdownsampledframe=imresize(im(k-1).gray, .125); %.25 for faces
difImage=downsampledframe-lastdownsampledframe;  %% computing difference in each pixel between current image and previous image
%motion = step(hbm, lastdownsampledframe, downsampledframe); 
%absmot=motion.^2;
sq=difImage.^2; %% square each difference
im(k).RMS=sqrt(mean(sq(:)));  %% sqrt of the mean of the squares (average measure of how much the luminance changed between last and current image)
%im(k).MOT=sqrt(mean(absmot(:)));
else
    im(k).RMS=0;  %% can't do this step if it is the first frame of the movie, obvi
    im(k).MOT=0;
end
rms=rms+im(k).RMS;  %% summing up the average luminance change for each pair
%cummot=cummot+im(k).MOT;
end
[mov(v).totalmotenergy, mov(v).leftmotenergy, mov(v).rightmotenergy, mov(v).netmotenergy,]=motionenergy(videovector');
mov(v).avgLum=m/k;  %% average luminance across whole video
mov(v).stdLum=stdev/k; %% average frame-wise luminance variance across whole video
mov(v).avgLumChange=rms/k   %% average change in luminance across whole video
%mov(v).avgMotion=cummot/k

save([stimdir '/stim_control_new.mat'], 'mov');
end

