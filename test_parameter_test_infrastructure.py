import pytest
from parameter_test_infrastructure import *
from glob import glob
import pandas as pd
import numpy as np

speccubefile = 'test_files/HD1160-KL20-speccube.fits'

def test_FWHMIOWA_calculator_broadband(speccubefile):
    FWHM = 6.0192456018518525
    OWA = 57.869643287037036

    with fits.open(speccubefile) as hdulist:
        fwhm, iwa, owa = FWHMIOWA_calculator(hdulist)

    equalfwhm = round(fwhm, 5) == round(FWHM, 5)
    equalowa = round(owa, 5) == round(OWA, 5)

    assert equalfwhm and equalowa

def test_calibrate_ss_contrast(speccubefile):
    wln_um = np.array([1.15956144, 1.19969705, 1.24122187, 1.28418397, 1.32863311, 1.37462076, 1.42220017,
                       1.47142643, 1.52235655, 1.5750495, 1.6295663, 1.68597007, 1.74432613, 1.80470206,
                       1.86716776, 1.93179558, 1.99866034, 2.06783947, 2.13941309, 2.21346406, 2.29007815, 2.36934405])

    spot_to_star = np.array([0.0048601, 0.00454035, 0.00424164, 0.00396258, 0.00370188, 0.00345833, 0.00323081,
                             0.00301825, 0.00281968, 0.00263417, 0.00246087, 0.00229897, 0.00214772, 0.00200642,
                             0.00187441, 0.0017511, 0.00163589, 0.00152826, 0.00142772, 0.00133379, 0.00124604,
                             0.00116406])

    with fits.open(speccubefile) as hdulist:
        wavelength, ratio = calibrate_ss_contrast(hdulist)

    equal_wlnum = np.round(wavelength, 5) == np.round(wln_um, 5)
    equal_spottostar = np.round(ratio, 5) == np.round(spot_to_star, 5)

    assert equal_wlnum and equal_spottostar

# Planet Injection Stuff
fake_fluxes = [5.0e-3, 1.0e-4]
fake_seps = [15, 30]
fake_PAs = [60, 240]

# Sample KLIP Parameters
annuli = [5, 10]
subsections = [2, 4]
movement = [1, 2]
numbasis = [3, 5]
spectrum = ['methane', None]

HD1160 = TestDataset(fileset='test_files/hd1160/*.fits', object_name='HD_11_60', mask_xy=[144,80],
                     fake_fluxes=fake_fluxes, fake_seps=fake_seps, annuli=annuli,
                     subsections=subsections, movement=movement, numbasis=numbasis,
                     spectrum=spectrum, mode='ADI+SDI', fake_PAs=fake_PAs)

def test_trial_list_build(td=HD1160):
    zero = td.trials[0] == Trial(5, 2, 1, 3, 'methane', 'ADI+SDI', None, None, None, None, None,
                                 None)
    fifteen = td.trials[15] == Trial(5, 4, 2, 5, None, 'ADI+SDI', None, None, None, None, None,
                                     None)
    twentyfive = td.trials[25] == Trial(10, 4, 1, 3, None, 'ADI+SDI', None, None, None, None, None,
                                     None)
    thirtyone = td.trials[31] == Trial(10, 4, 2, 5, None, 'ADI+SDI', None, None, None, None, None,
                                       None)
    assert zero and fifteen and twentyfive and thirtyone


def test_klip_parameter_string_creation():
    pass

def test_klipped_filepath_string_creation():
    pass

def test_get_contrast():
    pass

def test_detect_planets():
    pass

def test_pasep_to_xy():
    # modify this so that it is actually directly invoking the function instead of just using the same process
    same = []
    csvs = glob('detections/*.csv')
    for csv in csvs:
        df = pd.read_csv(csv)
        rads = np.array(df['PA']) / 180 * np.pi
        seps = np.array(df['Sep (pix)'])
        for i, j in enumerate(zip(rads, seps)):
            same.append(np.abs(-np.sin(j[0]) * j[1] - df['x'][i]) < 0.05)
            same.append(np.abs(np.cos(j[0]) * j[1] - df['y'][i]) < 0.05)

    assert np.sum(same) == len(same)

