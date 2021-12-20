from setuptools import setup

with open("requirements.txt") as requirements_file:
    requirements = [
        x.strip()
        for x in requirements_file.readlines()
        if not x.strip().startswith("#")
    ]

setup(
    name="cert_generator",
    version="0.0.1",
    py_modules=["main"],
    install_requires=requirements,
    entry_points={"console_scripts": ["cert_generator=main:main"]},
)
