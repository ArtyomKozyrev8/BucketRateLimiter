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
    packages=find_packages(exclude=["tests"]),
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
