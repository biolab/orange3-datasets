#!/usr/bin/env python

from setuptools import setup

MAJOR = 0
MINOR = 1
MICRO = 5
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

ENTRY_POINTS = {
    # Entry point used to specify packages containing tutorials accessible
    # from welcome screen. Tutorials are saved Orange Workflows (.ows files).
    'orange.widgets.tutorials': (
        # Syntax: any_text = path.to.package.containing.tutorials
        'exampletutorials = orangecontrib.datasets.tutorials',
    ),

    # Entry point used to specify packages containing widgets.
    'orange.widgets': (
        # Syntax: category name = path.to.package.containing.widgets
        # Widget category specification can be seen in
        #    orangecontrib/datasets/widgets/__init__.py
        'Datasets = orangecontrib.datasets.widgets',
    ),

    # Register widget help
    "orange.canvas.help": (
        'html-index = orangecontrib.datasets.widgets:WIDGET_HELP_PATH',)
}

KEYWORDS = [
    # [PyPi](https://pypi.python.org) packages with keyword "orange3 add-on"
    # can be installed using the Orange Add-on Manager
    "orange3 add-on",
    "world bank data",
    "indicator api",
]


def get_description():
    with open("README.rst") as f:
        return f.read()


if __name__ == '__main__':
    setup(
        name="Orange3-Datasets",
        version=VERSION,
        license="MIT",
        author="Miha Zidar",
        author_email="zidarsk8@gmail.com",
        description=("Orange interface for World Bank Data Indicator and "
                     "Climate APIs"),
        long_description=get_description(),
        url="https://github.com/biolab/orange3-datasets",
        download_url=("https://github.com/biolab/orange3-datasets/tarball/{}".format(VERSION)),
        packages=[
            'orangecontrib',
            'orangecontrib.datasets',
            'orangecontrib.datasets.tutorials',
            'orangecontrib.datasets.widgets',
        ],
        package_data={
            'orangecontrib.datasets': ['tutorials/*.ows'],
            'orangecontrib.datasets.widgets': ['icons/*'],
        },
        install_requires=[
            'Orange3',
            'numpy',
            'observable',
            'simple_wbd>=0.5.1',
        ],
        extras_require={
            'doc': [
                'sphinx',
                'sphinx_rtd_theme',
            ],
            'test': [
                'nose',
                'nose-cov',
            ]
        },
        entry_points=ENTRY_POINTS,
        keywords=KEYWORDS,
        namespace_packages=['orangecontrib'],
        include_package_data=True,
        zip_safe=False,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: X11 Applications :: Qt',
            'Environment :: Plugins',
            'Programming Language :: Python',
            'Operating System :: OS Independent',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'Intended Audience :: Developers',
        ],
    )
