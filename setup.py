from setuptools import setup, find_packages

setup(
    name="dungeon_history",
    version="0.1.0",
    author="mattdoug604",
    author_email="mattdoug604@gmail.com",
    packages=find_packages(),
    description="Randomly generate the history of a fantasy dungeon including it's creator, location, purpose, and current state.",
    url="https://github.com/mattdoug604/dungeon-history.git",
    python_requires=">=3",
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": ["dungeon-history = dungeon_history.dungeon_history:main"]
    },
)
