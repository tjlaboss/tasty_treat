# Error
#
# Custom errors for geometry builds

class FinalizedError(Exception):
	"""To be raised when a user tries to add something to pieces
	of a geometry which have already been finalized"""
	pass
