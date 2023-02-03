from setuptools import setup, find_packages

setup(
    name="db-requester",
    version="0.1",
    description="Test project for a job application",
    author="Dmitry Nikonov",
    author_email="no.i.am.married@gmail.com",
    packages=find_packages(),
    install_requires=[
        "pyyaml~=6.0",
        "pydantic~=1.10",
    ],
    entry_points={
        "console_scripts": [
            "db_requester = db_requester.main:main",
            "db_populate = db_requester.scripts.populate:main",
            "db_query = db_requester.scripts.query:main",
            "db_cleanup = db_requester.scripts.cleanup:main",
        ]
    },
)
