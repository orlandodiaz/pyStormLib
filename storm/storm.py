
# Python StormLib Wrapper
# by Vjeux <vjeuxx@gmail.com> http://blog.vjeux.com/

# API Documentation
# http://www.zezula.net/en/mpq/Stormlib.html

from ctypes import *
import os, re

storm = cdll.LoadLibrary(re.sub('/[^/]+$', '', __file__) + '/libStorm.so')

# Wrapper around storm to check for errors
class StormWrapper(type):
	def __getattr__(self, attr):
		return lambda *arguments: Storm.__call(func=getattr(storm, attr), *arguments)

	def __call(*arguments, **keywords):
		# Call the function
		func = keywords['func']
		ret = func(*arguments[1:])

		# Handle errors
		code = storm.GetLastError()
		if (code not in (0, 106, 107)): # "No more files" and "End of file" are not real errors
			message = code in MPQErrors and MPQErrors[code] or 'Error #%i' % code
			raise Exception(message)

		return ret

# MetaClass trick to be able to use Storm.<function name>()
class Storm:
	__metaclass__ = StormWrapper

MPQErrors = {
	10000: "ERROR_AVI_FILE No MPQ file, but AVI file.",
	10001: "ERROR_UNKNOWN_FILE_KEY Returned by SFileReadFile when can't find file key",
	10002: "ERROR_CHECKSUM_ERROR Returned by SFileReadFile when sector CRC doesn't match",
	10003: "ERROR_INTERNAL_FILE The givn operation is not allowed on internal file",

	0: "ERROR_NO_SIGNATURE SFileVerifyArchive: There is no signature in the MPQ",
	1: "ERROR_VERIFY_FAILED SFileVerifyArchive: There was an error during verifying signature (like no memory)",
	2: "ERROR_WEAK_SIGNATURE_OK SFileVerifyArchive: There is a weak signature and sign check passed",
	3: "ERROR_WEAK_SIGNATURE_ERROR SFileVerifyArchive: There is a weak signature but sign check failed",
	4: "ERROR_STRONG_SIGNATURE_OK SFileVerifyArchive: There is a strong signature and sign check passed",
	5: "ERROR_STRONG_SIGNATURE_ERROR SFileVerifyArchive: There is a strong signature but sign check failed",

	2: "ERROR_FILE_NOT_FOUND",
	1: "ERROR_ACCESS_DENIED",
	9: "ERROR_INVALID_HANDLE",
	12: "ERROR_NOT_ENOUGH_MEMORY",
	105: "ERROR_BAD_FORMAT",
	106: "ERROR_NO_MORE_FILES",
	107: "ERROR_HANDLE_EOF",
	95: "ERROR_NOT_SUPPORTED",
	22: "ERROR_INVALID_PARAMETER",
	28: "ERROR_DISK_FULL",
	17: "ERROR_ALREADY_EXISTS",
	108: "ERROR_CAN_NOT_COMPLETE",
	109: "ERROR_FILE_CORRUPT",
	10: "ERROR_INSUFFICIENT_BUFFER"
}

class MPQFileData(Structure):
	_fields_ = [
		('filename', c_char * 1024),
		('plainname', c_char_p),
		('hashindex', c_int, 32),
		('blockindex', c_int, 32),
		('filesize', c_int, 32),
		('fileflags', c_int, 32),
		('compsize', c_int, 32),
		('filetimelo', c_int, 32),
		('filetimehi', c_int, 32),
		('locale', c_int, 32)
	]

	def __repr__(self):
		return self.filename

	def __str__(self):
		return self.filename

class MPQ():
	mpq = c_int()

	def __init__(self, filename):
		"""Open a MPQ Archive"""
		Storm.SFileOpenArchive(filename, 0, 0x0100, byref(self.mpq))
	
	def close(self):
		"""Close the MPQ Archive"""
		Storm.SFileCloseArchive(self.mpq)

	def list(self, mask='*'):
		"""List all the files matching the mask"""

		# Initial Find
		file = MPQFileData()
		find = Storm.SFileFindFirstFile(self.mpq, mask, byref(file), None)
		yield file

		# Go through the results
		file = MPQFileData()
		while Storm.SFileFindNextFile(find, byref(file)):
			yield file
			file = MPQFileData()

	def extract(self, mpq_path, local_path=None):
		"""Extract a file"""

		# Handle arguments
		if isinstance(mpq_path, MPQFileData):
			mpq_path = mpq_path.filename
		if local_path is None:
			local_path = mpq_path
		
		# Create the directories
		local_path = local_path.replace('\\', '/')
		try:
			os.makedirs(re.sub('/[^/]+$', '', local_path))
		except Exception:
			pass

		# Extract!
		Storm.SFileExtractFile(self.mpq, mpq_path, local_path)

	def has(self, name):
		"""Does the MPQ have the file"""

		return Storm.SFileHasFile(self.mpq, name)
	
	def read(self, name):
		"""Read the file content"""

		# Handle argument
		if isinstance(name, MPQFileData):
			name = name.filename

		# Open the file
		file = c_int()
		Storm.SFileOpenFileEx(self.mpq, name, 0, byref(file))

		# Get the Size
		high = c_int()
		low = Storm.SFileGetFileSize(file, byref(high))
		size = int(high.value << 32) + low
		
		# Read the File
		data = c_buffer(size)
		read = c_int()
		Storm.SFileReadFile(file, data, size, byref(read), None)

		# Close and Return
		Storm.SFileCloseFile(file)
		return data.value;

