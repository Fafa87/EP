import setuptools
        
setuptools.setup(
        author="Filip Mroz",
        author_email="fafafft@gmail.com",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Topic :: Scientific/Engineering"
        ],
        cmdclass={},
        include_package_data=True,
        keywords=["evaluation","semantic","segmentation","benchmark"],
        license="BSD",
        long_description="",
        name="sep",
        description="Semantic Evaluation Platform",
        packages=setuptools.find_packages(exclude=[
            "tests", "examples"
        ]),
        setup_requires=[
            "pytest"
        ],
        url="https://github.com/Fafa87/EP/sep",
        version="0.0.1"
)