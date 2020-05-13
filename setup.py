import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xapi-data-analyzer-HBlanco36-wboettge",
    version="0.1",
    author="Harrison White and Walt Boettge",
    author_email="hwhite9@wisc.edu, wboettge@wisc.edu",
    description="A Python CLI tool to clean and analyze xAPI data. Intended for use at the University of Wisconsin - "
                "Madison using data from the DoIT xAPI Learning Locker.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HBlanco36/xapi-data-analyzer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'xapi-data-analyzer = xapi_data_analyzer.Main:main'
        ]
    },
    install_requires=[
        'pandas',
    ],
    python_requires='>=3.0',
)
