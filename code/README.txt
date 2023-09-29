To do this analysis, we did the following steps:

1) On the (https://gea.esac.esa.int/archive/)[Gaia archive], we ran the following ADQL query:

SELECT gaia.*, gaia_spec.*, gaia_full.ecl_lat, gaia_full.ecl_lon, gaia_full.nu_eff_used_in_astrometry, gaia_dist.r_med_geo, gaia_dist.r_lo_geo, gaia_dist.r_hi_geo, gaia_dist.r_med_photogeo, gaia_dist.r_lo_photogeo, gaia_dist.r_hi_photogeo, sdss.objid, sdss.mjd, sdss.g, sdss.dered_g, sdss.err_g, sdss.r, sdss.dered_r, sdss.err_r, sdss.i, sdss.dered_i, sdss.err_i
FROM gaiadr3.gaia_source_lite as gaia 
INNER JOIN gaiadr3.gaia_source as gaia_full ON gaia.source_id = gaia_full.source_id
INNER JOIN gaiadr3.xp_summary as gaia_spec ON gaia.source_id = gaia_spec.source_id
INNER JOIN external.gaiaedr3_distance as gaia_dist ON gaia.source_id = gaia_dist.source_id
INNER JOIN gaiadr3.sdssdr13_best_neighbour as sdss_neigh ON gaia.source_id = sdss_neigh.source_id
INNER JOIN external.sdssdr13_photoprimary as sdss ON sdss_neigh.original_ext_source_id = sdss.objid
WHERE gaia.has_xp_continuous = 'True' AND
sdss.err_g <= 0.01 AND
sdss.err_r <= 0.01 AND
sdss.err_i <= 0.01 AND
sdss.g - sdss.dered_g < 1.5 AND
gaia.parallax_over_error > 10

which selects from Gaia DR3, merged with Bailer-Jones et al. (2021) EDR3 distances, merged with SDSS DR13 photoprimary. We take all stars with XP spectra with SDSS photometric errors <1% in gri, with extinctions in g<1.5, and \varpi/\sigma_\varpi > 10. This gives us 10M stars, so to trim this a bit, we're going to cut further down on the quality of the XP spectral representation, which we do in `sample_preprep.ipynb`.

2) Because of this enormous resulting sample, we tried to separately download the XP spectral coefficients with astroquery, using the code in `get_spectra.ipynb`. This proved to be a very difficult thing to run from my laptop, so instead, we used GaiaXPy, which just takes a DR3 source id, and spits out the synthetic photometry in a given system. When we tried this on an older version of the query, that code was in `convert_spectra.ipynb`. Now we're going to run it from a bit of a beefier machine at UW with a better internet connection. That code is in `XP_download_convert.py`.

3) We then used the code in `obs_times.ipynb`, which takes the listed observation MJD from SDSS DR13 photoprimary, and converts to BJD, using the stars' coordinates and the location of APO. This is using astropy's Time functionality. We then used the ScanningLaw package (Everall et al. 2021) to get the mean Gaia observation time of each source using the nominal DR3 scanning law, and converted from onboard time to BJD using Gaia collab. 2016, eq (3).

4) Is where we start with our analysis, looking into systematics. We first load in the result of the Gaia archive queries. We code missing values of ag_gspphot and ebpminrp_gspphot and 0.0, and fill in SDSS photometry with missing values (-9999) as np.nan. Next we add a column for the dereddened G_BP-G_RP color: bp_rp_0. Next, we load in the synthetic photometry derived from the XP spectra; because the errors are in flux units, we derive a magnitude error for each band as 2.5 / ln(10) * sigma_(flux_band)/flux_band. Then we load in the observation time information. All three pandas dataframes (Gaia query, synthetic photometry, observation times) have 4598275 stars (4.6M!). We merge these dataframes together, and save them as `merged_sdss_gaia_with_bjds.csv`. Next, to toss some stars with junk SDSS photometry, we restrict the sample to stars brighter than 17th mag in all SDSS bands. To this filtered dataframe, we insert columns corresponding to 1e3 times the change in each band, divided by the timespan between the SDSS and mean Gaia observation BJDs, i.e., Delta mag per kyr. Finally, we add a column for the absolute G mag, using the median photogeometric B-J+21 distance, and ag_gspphot. This cleaned dataframe is saved as `cleaned_sample_with_dMag_per_time_and_MG.csv`

4) The main analysis is then in `CMD_distance.ipynb`. 

Some Trevor thoughts on systematics: what is mean delta_mag in each band as a function of G, and as a function of the uncorrected BP-RP? Might be a constant offset, or some trend to correct for.