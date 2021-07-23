from setuptools import setup

from fastapi_vers import __version__


setup(
    name="fastapi_vers",
    version=__version__,
    author="Roma Koshel",
    author_email="roma.koshel@gmail.com",
    license="MIT",
    py_modules=["fastapi_vers"],
    include_package_data=True,
    install_requires=[
        "fastapi>=0.62.0",
        "packaging",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
)
