import setuptools

setuptools.setup(
        author="Filip Mroz",
        author_email="fafafft@gmail.com",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.7",
            "Topic :: Scientific/Engineering"
        ],
        include_package_data=True,
        install_requires=[
            "matplotlib>=1.4.0",
            "Pillow>=2.5.3"
        ],
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
        version="1.0.1"
)