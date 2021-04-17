import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="erddap-python",
    version="0.0.6b",
    author="Favio Medrano",
    author_email="hmedrano@cicese.mx",
    description="Python erddap API client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['pandas', 'requests', 'xarray', 'netCDF4'],
    url="https://github.com/hmedrano/erddap-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT',
    python_requires='>=3.6',
)
