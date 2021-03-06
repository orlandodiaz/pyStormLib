[pyStormLib](http://blog.vjeux.com/) - python wrapper for StormLib
================================

Python Wrapper for [Zezula StormLib](http://www.zezula.net/en/mpq/stormlib.html) that manages MPQ files. It covers all the Read abilities of StormLib.

It is being used in production at [db.mmo-champion.com](http://db.mmo-champion.com/). Feel free to drop me a message if you are using it :)

Licence: [Do What The Fuck You Want To Public License](http://sam.zoy.org/wtfpl/)

API
---
* **MPQ**(path): Open a MPQ

* **list**(mask='*'): List of all the files matching the mask

* **read**(path): Content of the file

* **has**(path): Does the MPQ have the file?

* **extract**(mpq_path, local_path=mpq_path): Extract a file.
    * mpq_path can be a file returned by **list**()

* **patch**(patch_files, prefix): Add MPQs as patch source.
    * patch_files can either be a string that will be considered as a glob or an array of paths
    * See [StormLib Documentation](http://www.zezula.net/en/mpq/stormlib/sfileopenpatcharchive.html) for the prefix option.

Example
-------
Random usage

```python
from storm import MPQ

mpq = MPQ('wow-update-13316.MPQ')

print '[list] List TXT and ANIM files'
print list(mpq.list('*.txt')) + list(mpq.list('*.anim'))

print '[extract] Extracting all the enUS DBC'
for file in mpq.list('enUS*.dbc'):
	print file
	mpq.extract(file, 'extract/' + str(file))

print '[read] Reading a few TXT'
for file in mpq.list('en*.txt'):
	print file
	print mpq.read(file)
```

Extract all the DBC files applying the patch files.

```python
from storm import MPQ

mpq = MPQ('../wow/enGB/locale-enGB.MPQ')
mpq.patch('../wow/wow-update-*.MPQ', 'enGB')

for file in mpq.list('*.dbc'):
	mpq.extract(file)
```

Installation
=======

* Download and Compile the latest version of StormLib: http://www.zezula.net/en/mpq/download.html
* Put stormLib.so in the storm/ folder

Here's a sample command line explanation

```
wget http://www.zezula.net/download/stormlib_beta.zip
unzip stormlib_beta.zip
cd StormLib
mv Makefile.linux Makefile
make
cp libStorm.so ../storm/
```