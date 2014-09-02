#! /opt/local/bin/python
import flowml as fml
import argparse


def batch_tsne(fnames, sample):
	fdarray = []
	for fname in fnames:
		fdarray.append(fml.FlowData(fname))

	fml.tsne(fdarray, 'visne', sample = sample, verbose = True)
	
	for fd, fname in zip(fdarray, fnames):
		fd.fcs_export(fname[0:-4]+'_visne.fcs')


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=("Run viSNE on specified FCS "
				"files and return new FCS files with the viSNE embedding "
				"in two new columns."))

	parser.add_argument('files', metavar = 'FCS', type = str, nargs = '+',
			help = 'FCS file to be processed')

	parser.add_argument('--sample', dest='sample', action='store',
			type = int, help = "number of samples to take",
			default = 20000)

	args = parser.parse_args()	
	fnames = args.files
	sample = args.sample

	batch_tsne(fnames, sample)
