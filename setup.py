from setuptools import setup


setup(
    name="fastapi_vers",
    version="0.1.1",
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
