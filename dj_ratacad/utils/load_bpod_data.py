import scipy.io
import mat73
import numpy as np


def load_bpod_data(filename):
    """Loads Bpod data file as a dictionary

    Parameters
    ----------
    filename : str
        path to Bpod data file
    """

    try:
        bpod_data = mat73.loadmat(filename)
    except:
        try:
            raw = scipy.io.loadmat(filename, squeeze_me=True, chars_as_strings=True)
            bpod_data = recarray_to_dict(raw["SessionData"])
        except:
            bpod_data = None

    return bpod_data


def recarray_to_dict(ra):
    """Convert bpod raw data loaded using scipy.io.loadmat to dictionary

    Parameters
    ----------
    raw_data : dict
    """

    if ra is not None:

        data_dict = {}

        for n in ra.dtype.names:

            this = ra[n][()]

            if (type(this) == np.ndarray) and (this.dtype.names is not None):
                this = recarray_to_dict(this)

            data_dict[n] = this

        return data_dict

    else:

        return None
