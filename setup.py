from setuptools import setup

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
    url=''
)
