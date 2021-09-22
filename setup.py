from setuptools import setup, find_packages

setup(
    name='tagger',
    version='0.1',
    description='Easier modification of audio file metadata tags (hopefully)',
    license='TODO',
    packages=['tagger'],
    author='Evan MacTaggart',
    author_email='evan.mactaggart@gmail.com',
    install_requires=['mutagen', 'click'],
    keywords=['id3', 'mp3', 'm4a', 'flac', 'audio', 'tags', 'metadata'],
    url='https://github.com/emactaggart/tagger',
    entry_points={
        'console_scripts':['tagger=tagger:start']
    }
)
