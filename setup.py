from setuptools import setup

setup(
    name='snapshotalyzer-2019',
    version='0.1',
    author='Yuri Maftei',
    author_email='iuri1877@hotmail.com',
    description="Snapshotalyzer 2019 is a tool to manage AWS EC2 snapshots",
    license="GPLv3+",
    packages=['shotty'],
    url="https://github.com/justtech1877/snapshotalyzer-2019",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        shotty=shotty.shotty:cli
    ''',

)
