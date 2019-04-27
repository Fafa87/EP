import setuptools


class Test(setuptools.Command):
    user_options = [
        ("pytest-args=", "a", "arguments to pass to py.test")
    ]

    def initialize_options(self):
        self.pytest_args = []

    def finalize_options(self):
        pass

    def run(self):
        import pytest
        import sys
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)
        
setuptools.setup(
        author="Filip Mroz",
        author_email="fafafft@gmail.com",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.7",
            "Topic :: Scientific/Engineering"
        ],
        cmdclass={
            "test": Test
        },
        include_package_data=True,
        keywords=["evaluation","precision","recall"],
        license="BSD",
        long_description="",
        name="Evaluation Platform",
        description="",
        packages=setuptools.find_packages(exclude=[
            "tests", "examples"
        ]),
        setup_requires=[
            "pytest"
        ],
        url="https://github.com/Fafa87/EP",
        version="1.1.0"
)