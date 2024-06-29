"""
This module contains the implementation of the Cache abstract base class and its
file-based implementation.

The Cache abstract base class is an interface for caching data. It provides
methods for checking if a key exists in the cache, getting the value associated
with a key, and setting the value associated with a key.

The FileCache class is an implementation of the Cache abstract base class that
stores the cache data in a file. The data is stored in JSON format in the file
located at the path provided in the constructor.
"""
