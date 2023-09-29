from gaiaxpy import generate, PhotometricSystem
import pandas as pd
import numpy as np
from tqdm import tqdm
import warnings

#Thx StackOverflow user Boris Verkhovskiy, chunks a list up into X-sized chunks
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

#Some setup: read in the query source ids, 
query = 'DR3_SDSS_spectra_cleaned_sourceids_092723.csv'
query_df = pd.read_csv(query)
sids = list(query_df.source_id.values)
done = pd.Index(np.array([]))
data = []

#Tell GaiaXPy we want the SDSS photometric system, corrected for systematic offsets
phot_system = PhotometricSystem.SDSS_Std

#Loop over chunks of 5000 source ids (the archive limit)
#Some of this code is a remnant from when this was run from a notebook, which would sometimes crash
#so I would re-run this cell, and skip chunks that were already done
for j in tqdm(chunker(sids, 5000), total=len(sids)//5000):
    j_s = pd.Index(np.array(j))
    if np.all(j_s.isin(done)):
        continue # do some pandas magic to make sure we're not looking at a duplicate chunk
    generated_data = generate(j, phot_system, error_correction=True, save_file=False) # generate the photometry
    # note, error_correction=True handles underestimated uncertainties in the photometry 
    data.append(generated_data) #append photometry to our output list
    done = done.append(j_s) #append source ids to our list to check against
    
out_df = pd.concat(data)
out_df.to_csv('synthetic_SDSS_cleaned_sample.csv', index=False)