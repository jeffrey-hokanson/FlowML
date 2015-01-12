#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# Library for reading and writing FCS files
import re
import numpy as np
import sys
import os
debug = False
#debug = True


# TODO: remove error text message and replace with raising exceptions

# TODO: Implement read only header
def read(filename, convert_metadata = True, only_header = False, debug = False):
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

    if debug:
        import pprint

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

    hdr_start = int(first_line[10:18])
    hdr_stop = int(first_line[18:26])
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
    status = f.seek(hdr_start)
    header = f.read(hdr_stop - hdr_start + 1)

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

    if debug:
        print data_type

    # https://stackoverflow.com/questions/14245094/how-to-read-part-of-binary-file-with-numpy
    f.seek(data_start, os.SEEK_SET)
    
    if len(data_type) == 1:
        data = np.fromfile(f, dtype=data_type[0], count = n_parameters*n_events)
        assert data.shape[0] == n_parameters*n_events, "Read only %d entries; expected %dx%d matrix." % (data.shape[0], n_events, n_parameters)
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



def write(filename, data, metadata, analysis = None, version = '3.1'):
    """Write an FCS with name `filename`
    data - numpy array
    metadata - dictionary of key-value pairs containing metadata
    """
    # This follows Jacob Frelinger's implementation
    # https://github.com/jfrelinger/fcm/blob/master/src/io/export_to_fcs.py
    if version != '3.1':
        raise NotImplementedError

    if analysis is not None:
        raise NotImplementedError 

    ###########################################################################    
    # First stage: check the formatting of the metadata segment, writing
    # values specific to the data provided
    ###########################################################################    
    
    # Set all key names in the metadata dictionary to upper case to aid in 
    # checking for key existance.  FCS file requires that keys are case
    # insenstive, whereas values are case sensitive
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

    # If there is no analysis segment, both of these values are '0'
    if analysis is None:
        metadata['$BEGINANALYSIS'] = str(0)
        metadata['$ENDANALYSIS'] = str(0)
    
    # Multiple datasets per file is now discouraged, so we do not support
    # this feature.  We indicate by setting the location where the next dataset
    # starts to zero.
    metadata['$NEXTDATA'] = str(0)
    
    # Number of columns in our dataset
    metadata['$PAR'] = str(data.shape[0])
    metadata['$TOT'] = str(data.shape[1])

    # Set the data properties: byte length and endian-ness
    if data.dtype.kind == 'f':
        # Endian-ness setting.  We use a dictionary in place of a switch
        # statement.  '|' refers classes of data which lack endian-ess,
        # but floats should always have endian-ness.
        byteorder_dict = {'<': '1,2,3,4', '>': '4,3,2,1', '|': 'ERR'}
        if sys.byteorder == 'little':
            byteorder_dict['='] = '1,2,3,4'
            #byteorder_dict['='] = '4,3,2,1'
        else:
            byteorder_dict['='] = '4,3,2,1'
            #byteorder_dict['='] = '1,2,3,4'
        
        metadata['$BYTEORD'] = byteorder_dict[data.dtype.byteorder]
        assert metadata['$BYTEORD'] is not 'ERR', \
            'Unknown datatype {}'.format(data.dtype)
        
        # set the number of bits in the data
        if data.dtype.itemsize*8 == 32:
            metadata['$DATATYPE'] = 'F'
            nbits = 32
        elif data.dtype.itemsize*8 == 64:
            metadata['$DATATYPE'] = 'D'
            nbits = 64
        else:
            assert False, """Float datatype {} of length {} not 
                supported""".format(data.dtype, data.dtype.itemsize)

        # Now assign the proper number of bits per each channel
        for j in range(data.shape[0]):
            metadata['$P{}B'.format(j+1)] = str(nbits)
        
    elif data.dtype.kind == 'i':
        raise NotImplementedError 


    # Currently, we assume we can fit the TEXT segment in the first 99,999,999 bytes
    # so we do not use the supplemental TEXT segment option
    metadata['$BEGINSTEXT'] = str(0)
    metadata['$ENDSTEXT'] = str(0)

    # Set the mode: we only support list mode:
    metadata['$MODE'] = 'L'
   
    for j in range(int(metadata['$PAR'])):
        # Check every channel has an amplification
        amp_key = '$P{}E'.format(j+1)
        if metadata['$DATATYPE'] in ['F', 'D'] or amp_key not in metadata:
            metadata[amp_key] = '0,0'
        # Check every channel has a range set
        range_key = '$P{}R'.format(j+1)
        if range_key not in metadata:
            # We use nanmax to avoid issues with undefined values 
            metadata[range_key] = str(int(np.nanmax(data[:,j])))


    ###########################################################################    
    # Second stage: simulate writing to locate positions of data in file
    ###########################################################################    
    
    # FCS defined positions 
    # Borrowed from FCM under BSD Simplified 2 Clause
    hdr_text_start = (10, 17)
    hdr_text_end = (18, 25)
    hdr_data_start = (26, 33)
    hdr_data_end = (34, 41)
    hdr_analysis_start = (42, 49)
    hdr_analysis_end = (50, 57)

    text_start = 98    # Arbitrary start point; only somewhere after the end of the header

    # Generate text segment
    delimiter = '/' # delimiter between key-value pairs in TEXT segment
    def generate_text(metadata):
        text = ''    # starts with a delimiter
        for key, value in metadata.iteritems():
            assert isinstance(value,str), \
                "Key {}:{} is not a string".format(key,value)
            text += delimiter + key + delimiter + value 
        text += delimiter
        return text 
    
    # determine length of datasegement
    if metadata['$DATATYPE'] == 'F':
        data_length = int(metadata['$TOT'])*int(metadata['$PAR'])*4
    elif metadata['$DATATYPE'] == 'D':
        data_length = int(metadata['$TOT'])*int(metadata['$PAR'])*8

    # determine length of text segment
    text = generate_text(metadata)
    while True:
        text_length = len(text)
        data_start = text_start + text_length 
        data_end = data_start + data_length - 1
        metadata['$BEGINDATA'] = str(data_start)
        metadata['$ENDDATA'] = str(data_end)
        text = generate_text(metadata)
        if len(text) == text_length:
            break

    
    ###########################################################################    
    # Third stage: actually write the file
    ###########################################################################    
    f = open(filename, 'wb')

    # Write the start of the header.  We will fill in the values later.
    f.write('FCS3.1')
    f.write(' ' * 53)
    
    
    str_text_start = "{:8d}".format(text_start)
    f.seek(hdr_text_start[0])
    assert len(str_text_start)<= 8,"TEXT segment starts too far into file"
    f.write(str_text_start)

    text_end = text_start + len(text) - 1
    str_text_end = "{:8d}".format(text_end)
    f.seek(hdr_text_end[0])
    assert len(str_text_end) <= 8,"TEXT segment too long"
    f.write(str_text_end)

    str_data_start = "{:8d}".format(data_start)
    str_data_end = "{:8d}".format(data_end)

    if len(str_data_start) <= 8 and len(str_data_end) <= 8: 
        f.seek(hdr_data_start[0])
        f.write(str_data_start)
        f.seek(hdr_data_end[0])
        f.write(str_data_end)
    else:
        f.seek(hdr_data_start[0])
        f.write("{:8d}".format(0))
        f.seek(hdr_data_end[0])
        f.write("{:8d}".format(0))

    if analysis is None:
        f.seek(hdr_analysis_start[0])
        f.write("{:8d}".format(0))
        f.seek(hdr_analysis_end[0])
        f.write("{:8d}".format(0))


    # Write the TEXT segment
    
    # write spaces between end of header and start of text
    f.seek(58)
    f.write(' ' * (text_start - f.tell()))

    # write the header
    f.seek(text_start)
    f.write(text)

    # write the data
    #f.seek(text_end)
    #f.write(' '*(data_start - text_end))
    f.seek(data_start)
    # to fix ordering problems
    f.write(data.tostring('F'))
   
    # end the writing 
    f.close()    
    
