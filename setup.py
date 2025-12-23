from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A collection of Python tools and functions for human movement detection."

setup(
    name="bio-mvmt",
    version="0.0.1",
    author="joel deerwester",
    author_email="jdeerwester@gradcenter.cuny.edu",
    description="A collection of Python tools and functions for human movement detection.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jd2504/mvmt-detection",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib"
    ],
)
