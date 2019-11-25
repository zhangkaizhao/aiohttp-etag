import os
import re

from setuptools import setup


with open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'aiohttp_etag', '__init__.py'), 'r', encoding='latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'$", fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


install_requires = ['aiohttp']


setup(name='aiohttp-etag',
      version=version,
      description=("Etag support for aiohttp.web"),
      long_description=read('README.rst'),
      long_description_content_type='text/x-rst',
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: AsyncIO',
      ],
      author='Kaizhao Zhang',
      author_email='zhangkaizhao@gmail.com',
      url='https://github.com/zhangkaizhao/aiohttp-etag',
      license='Apache 2',
      packages=['aiohttp_etag'],
      python_requires=">=3.5",
      install_requires=install_requires,
      include_package_data=True)
