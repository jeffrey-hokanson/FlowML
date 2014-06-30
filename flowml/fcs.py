#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# Library for reading and writing FCS files
import re
import numpy as np

debug = False
#debug = True

if debug:
    import pprint

# TODO: remove error text message and replace with raising exceptions

def read(filename, convert_metadata = True):
    """
        Reads in an FCS file, given by filename and returns a tuple containing
        a numpy array and a dictionary of data.

        convert_metadata - convert the metadata into python appropreate types
            i.e., the string '15' becomes the integer 15

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



def save(filename, data, metadata, analysis = None, meta_analysis = None):

    raise NotImplementedError



# TODO: Remove this primative testing code in favor of a more professional version
if __name__ == '__main__':
    (data, metadata) = read('test.fcs')
    import pprint
    pp = pprint.PrettyPrinter(indent = 4)
    pp.pprint(data)
    pp.pprint(metadata)
