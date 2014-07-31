#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# Library for reading and writing FCS files
import re
import numpy as np
import sys
debug = False
#debug = True

if debug:
    import pprint

# TODO: remove error text message and replace with raising exceptions

def read(filename, convert_metadata = True):
    """Read in an FCS file and return numpy arrays of data and dictionaries of
    metadata

    Input arguments:
    filename -- file to read
    convert_metadata -- converts integer values stored as strings in the metadata

    Output:
    data -- numpy array of values in the data matrix
    metadata -- dictionary of metadata associated with the data segment
    analysis -- numpy array of values in the analysis matrix
    meta_analysis -- dictionary of metadata associated with the analysis segment
    
    Based on Laszlo Balkay's fca_readfcs.m from 3 Dec 2013.
    """
    f = open(filename, 'r')

    # Read the header information
    first_line = f.read(64)
    fcs_type = first_line[0:6]

    if debug:
        print fcs_type

    if fcs_type == 'FCS1.0':
        f.close()
        raise Exception("Cannot read FCS1.0 Files")
    elif fcs_type == 'FCS2.0' or fcs_type == 'FCS3.0' or fcs_type == 'FCS3.1':
        pass
    else:
        f.close()
        raise Exception('Error: File type {} not understood'.format(fcs_type)) 

    header_start = int(first_line[10:18])
    header_stop = int(first_line[18:26])
    data_start = int(first_line[26:34])
    data_stop = int(first_line[34:42]) 
    # Optional analysis section
    try:    
        analysis_start = int(first_line[42:50])
        analysis_stop = int(first_line[50:58])
    except ValueError:
        analysis_start = None
        analysis_stop = None
    
    ############################################################################
    # Read in the TEXT section
    ############################################################################
    status = f.seek(header_start)
    header = f.read(header_stop - header_start + 1)

    # The first character of the primary text segments contains the delimiter
    # We use re.escape to escape possible problem characters, e.g., [\*$^]
    delimiter = re.escape(header[0])
    
    # Now read in the metadata from the header into a dictionary
    # This pattern matches slashes: pattern = re.compile(r"/([^/]+)/([^/]*)(?=/[^/]+/|$)")
    # See: http://stackoverflow.com/questions/10380992/get-python-dictionary-from-string-containing-key-value-pairs
    # Match strings between delimiters and end with either end of file or a final delimiter
    pattern = re.compile(delimiter+r"([^"+delimiter+r"]+)"+delimiter+r"([^"+delimiter+r"]*)(?="+delimiter+"|$)")
    m = re.match(pattern,header)
    metadata = dict(pattern.findall(header))
    

    # TODO Include special code for reading in compensation matrices
    # NOTE Rather than following Balkay's approach, we keep all key-value pairs 
    #     from the TEXT section in a dictionary.
    
    ############################################################################
    # Read in the DATA section
    ############################################################################
    f.seek(data_start)
    n_events = int(metadata['$TOT'])
    n_parameters = int(metadata['$PAR'])
    
    if debug:
        print "# events: %d; # parameters %d" % (n_events,n_parameters)
        pp = pprint.PrettyPrinter(indent = 4)
        pp.pprint(metadata)


    # Types of Data: doubles, floats, and ints
    # We create a list for the case of 
    data_type = []
    if metadata['$DATATYPE'].lower() == 'd':
        data_type.append(np.dtype('float64'))
    elif metadata['$DATATYPE'].lower() == 'f':
        data_type.append(np.dtype('float32'))
    elif metadata['$DATATYPE'].lower() == 'i':
        for j in range(0,n_parameters):
            key = "$P{:d}B".format(j+1)
            bits = int(metadata[key])
            if bits == 16 or bits == 32 or bits == 64:
                data_type.append(np.dtype('uint{:d}'.format(bits)))
            else:
                raise Exception("Incompatable number of bits in channel {:d}, only allow 16, 32, or 64 bit data".format(bits))

    if debug:
        print data_type

    # Now factor in endian-ness
    if metadata['$BYTEORD'] == '1,2,3,4':
        # Little endian
        
        #data_type = data_type.newbyteorder('L')
        data_type = [x.newbyteorder('L') for x in data_type]
    elif metadata['$BYTEORD'] == '4,3,2,1':
        # Big endian
        # data_type = data_type.newbyteorder('B')
        data_type = [x.newbyteorder('B') for x in data_type]
    
    # TODO Cludges for nonstandard implementations of the standard 
    if metadata['$MODE'].lower() == 'u' or metadata['$MODE'].lower() == 'c':
        raise Exception("Importing a histogram depricated")
    elif metadata['$MODE'].lower() != 'l':
        raise Exception("Mode not understood")
    
    # Read in data
    # For interger types, we allow a bit length dependent on the channel; first, check if we 
    # only have one type
    if all(x == data_type[0] for x in data_type):
        data_type = [data_type[0]]

    if len(data_type) == 1:
        data = np.fromfile(f, dtype=data_type[0], count = n_parameters*n_events)
        data = data.reshape(n_parameters,n_events,order='F').copy()
    else:
        # We need a separate data type for each parameter
        data = []
        for j in range(0,n_parameters):
            data.append(np.fromfile(f,dtype=data_type[j], count=n_events))
   
    # TODO: Read analysis section of file

    analysis = None
    meta_analysis = None



    if convert_metadata:
        metadata['$TOT'] = int(metadata['$TOT'])
        metadata['$PAR'] = int(metadata['$PAR'])





    return (data, metadata, analysis, meta_analysis)



def write(filename, data, metadata, analysis = None, meta_analysis = None, version = '3.1'):
    """Write an FCS with name `filename`
    data - numpy array
    metadata - dictionary of key-value pairs containing metadata
    """
    # This follows Jacob Frelinger's implementation
    # https://github.com/jfrelinger/fcm/blob/master/src/io/export_to_fcs.py
    if version != '3.1':
        raise NotImplementedError
 
    f = open(filename, 'wb')


    # FCS defined positions 
    # Borrowed from FCM under BSD Simplified 2 Clause
    header_text_start = (10, 17)
    header_text_end = (18, 25)
    header_data_start = (26, 33)
    header_data_end = (34, 41)
    header_analysis_start = (42, 49)
    header_analysis_end = (50, 57)

    # Write the start of the header.  We will fill in the values later.
    f.write('FCS3.1')
    f.write(' ' * 53)
    
    # Write the TEXT segment
    text_start = 256    # Arbitrary start point; only somewhere after the end of the header
    delim = '/' # delimiter between key-value pairs in TEXT segment
    
    # write spaces between end of header and start of text
    f.seek(58)
    f.write(' ' * (text_start - f.tell()))
    

    # Set all key names in the metadata dictionary to upper case to aid in 
    # checking for key existance
    _metadata = {}
    for key, value in metadata.items():
        upper_key = key.upper()
        # Convert integers over to strings
        if isinstance(value, int):
            value = str(value)
        # Check that we do get a string 
        assert isinstance(value,str), \
            'Dictionary values must be strings, key {} is not'.format(upper_key)
        _metadata[upper_key] = value
    metadata = _metadata

    # Set required keys to proper values
    if analysis is None:
        metadata['$BEGINANALYSIS'] = str(0)
        metadata['$ENDANALYSIS'] = str(0)
    
    # Currently, we don't support multiple datafiles within the same file.
    metadata['$NEXTDATA'] = str(0)
    
    # Number of columns in our dataset
    metadata['$PAR'] = str(data.shape[0])
    metadata['$TOT'] = str(data.shape[1])

    # Set the data properties (byte length (i.e., single/double), endian, etc.)
    if data.dtype.kind == 'f':
        # Endian-ness setting
        byteorder_dict = {'<': '1,2,3,4', '>': '4,3,2,1', '|': 'ERR'}
        if sys.byteorder == 'little':
            byteorder_dict['='] = '1,2,3,4'
        else:
            byteorder_dict['='] = '4,3,2,1'

        metadata['$BYTEORD'] = byteorder_dict[data.dtype.byteorder]
        assert metadata['$BYTEORD'] is not 'ERR', \
            'Unknown datatype {}'.format(data.dtype)
        
        # set the number of bits in the data
        if data.dtype.itemsize*8 == 32:
            metadata['$DATATYPE'] = 'F'
            nbits = 32
        elif data.dtype.itemize*8 == 64:
            metadata['$DATATYPE'] = 'D'
            nbits = 64
        else:
            assert False, "Float datatype {} of length {} not supported".format(
                data.dtype, data.dtype.itemsize)

        # Now assign the proper number of bits per each channel
        for j in range(data.shape[0]):
            metadata['$P{}B'.format(j+1)] = nbits
        
    elif data.dtype.kind == 'i':
        raise NotImplementedError 


    # Currently, we assume we can fit the TEXT segment in the first 99,999,999 bytes
    # so we do not use the supplemental TEXT segment option
    metadata['$BEGINSTEXT'] = 0
    metadata['$ENDSTEXT'] = 0

    # Set the mode: we only support list mode:
    metadata['$MODE'] = 'L'



# TODO: Remove this primative testing code in favor of a more professional version
if __name__ == '__main__':
    (data, metadata, analysis, meta_analysis) = read('test.fcs')
    import pprint
    pp = pprint.PrettyPrinter(indent = 4)
    pp.pprint(data)
    pp.pprint(metadata)
