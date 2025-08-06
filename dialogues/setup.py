from setuptools import setup, find_packages

setup(
    name="dialogues",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "openai",
        "pyautogen"
    ],
    entry_points={
        "console_scripts": [
            "dialogues=main:main"
        ]
    },
)
