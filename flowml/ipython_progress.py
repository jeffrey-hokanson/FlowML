from __future__ import division
import uuid
from IPython.display import HTML, Javascript, display
import time
from datetime import datetime, timedelta


def progress_bar(iterator, expected_size = None, update_every = 10):

	pb_id = str(uuid.uuid4())
	pb_text = str(uuid.uuid4())
	pb = HTML(
	"""
	<div>
	<div style="border: 1px solid black; width:500px">
	  <div id="%s" style="background-color:red; width:0%%">&nbsp;</div>
	</div> 
	<div id="%s">
	Hello world
	</div>
	</div>
	""" % (pb_id, pb_text) )

	display(pb)
	count = len(iterator) if expected_size is None  else expected_size
	
	# Start time
	start = datetime.now()
	for i, item in enumerate(iterator):
		yield item
		if i % update_every == 0:
			display(Javascript("$('div#%s').width('%f%%')" % (pb_id, i/count*100)))
			if i > 0:
				current = datetime.now()
				delta = (current-start)
				left = ((count-i)/i)* delta.seconds
				hours = left//3600
				left = left - (hours*3600)
				minutes = left//60
				seconds = left - (minutes*60)
				remain = '%02d:%02d:%02d' % (hours, minutes, seconds)
			else:
				remain = ''

			display(Javascript("$('div#%s').text('%i of %i; done in %s')" % (pb_text, i, count, remain)))

	# Final display
	i = count
	current = datetime.now()
	delta = (current - start)
	left = ((count-i)/i)* delta.seconds
	hours = left//3600
	left = left - (hours*3600)
	minutes = left//60
	seconds = left - (minutes*60)
	remain = '%02d:%02d:%02d' % (hours, minutes, seconds)
	
	display(Javascript("$('div#%s').width('%f%%')" % (pb_id, i/count*100)))
	display(Javascript("$('div#%s').text('%i of %i; Finished in %s')" % (pb_text, i, count, remain)))

