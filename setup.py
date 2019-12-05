import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = [
        line.split(" ")[0]
        for line in f.read().splitlines()
        if not (line.startswith("-") or line.startswith("#"))
    ]

setuptools.setup(
    name="logma",
    version="0.0.3",
    author="peakiq",
    description="defaults for structlog",
    long_description=long_description,
    url="https://github.com/peakiq/logma",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    include_package_data=True,
    package_dir={"": "src"},
    # https://setuptools.readthedocs.io/en/latest/setuptools.html#find-namespace-packages
    packages=setuptools.find_namespace_packages(where="src"),
    install_requires=[required],
)
