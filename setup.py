import os
from setuptools import setup, find_packages
from importlib.machinery import SourceFileLoader


module = SourceFileLoader(
    "bucketratelimiter", os.path.join("bucketratelimiter", "version.py")
).load_module()


setup(
    name=module.__name__,
    version=module.__version__,
    author=module.__author__,
    author_email=module.author_email,
    license=module.package_license,
    description=module.package_info,
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
    platforms="all",
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Topic :: Internet",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Microsoft",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    packages=find_packages(exclude=["tests", "examples"]),
    package_data={"bucketratelimiter": ["py.typed"]},
    install_requires=[],
    python_requires=">=3.6, <4",
    extras_require={
        "develop": [
            "mypy",
            "pytest-cov",
            "pytest-asyncio",
        ],
    },
    project_urls={
        "Documentation": "https://github.com/ArtyomKozyrev8/BucketRateLimiter/",
        "Source": "https://github.com/ArtyomKozyrev8/BucketRateLimiter/",
    },
)
