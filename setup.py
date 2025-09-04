from setuptools import setup, find_packages

setup(
    name="regen88_codex",
    version="0.1.0",
    author="Commander X — Codex Dominion",
    description="Flame Correction Engine for All88 Systems",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[],
    tests_require=['pytest'],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
) 
