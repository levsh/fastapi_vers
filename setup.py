from setuptools import setup


def get_version():
    with open("fastapi_vers.py", "r") as f:
        for line in f.readlines():
            if line.startswith("__version__ = "):
                return line.split("=")[1].strip().strip('"')
    raise Exception("Can't read version")


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="fastapi_vers",
    version=get_version(),
    author="Roma Koshel",
    author_email="roma.koshel@gmail.com",
    description="FastAPI versioning",
    long_description=long_description,
    long_description_content_type="text/markdown",
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
