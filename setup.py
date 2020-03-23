import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="logma",
    version="0.3.0",
    author="peakiq",
    description="defaults for structlog",
    long_description=long_description,
    long_description_content_type='text/markdown',
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
    install_requires=["structlog"],
    extras_require={"tests": ["pytest", "pytest-cov", "pytest-watch"]},
)
