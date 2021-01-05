import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyerddap",
    version="0.0.1",
    author="Favio Medrano",
    author_email="hmedrano@cicese.mx",
    description="Python erddap API library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hmedrano/pyerddap",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)