from parameter_test_infrastructure import *
import warnings
from time import time
from numpy import floor

start = time()
warnings.simplefilter('ignore', category=RuntimeWarning)

# Describe Fake Planets To Be Injected
fake_fluxes = [5e-3, 1e-3, 5e-4, 1e-4, 5e-5]
fake_seps = [20, 30, 40, 50, 60]

# KLIP Parameters To Be Sampled
annuli = 7
subsections = 4
movement = 1
numbasis = 20

# Filelist(s) & Associated Mask(s)
hr8799_fileset = 'HR8799_cubes/*.fits'
hr8799_mask = None

# Create TestDataset For Each Set of Observations, e.g. hd = TestDataset('hd1160/*.fits', ...)
hr8799 = TestDataset(fileset=hr8799_fileset, object_name='HD1160', mask_xy=hr8799_mask,
                 fake_fluxes=fake_fluxes,fake_seps=fake_seps, annuli=annuli,
                 subsections=subsections, movement=movement, numbasis=numbasis)

# Have TestDataset Go To Town
hr8799.inject_fakes()
hr8799.run_KLIP()
hr8799.contrast_and_detection()

# Print Out Time Taken
end = time()
time_elapsed = end - start
hours = int(floor(time_elapsed / 3600))
remaining_time = time_elapsed - (hours * 3600)
minutes = int(floor(remaining_time / 60))
seconds = round(remaining_time - minutes * 60)

print("##################### TIME ELAPSED: {0} Hours, {1} Minutes, "
      "{2} Seconds #####################".format(hours, minutes, seconds))