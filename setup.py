import setuptools

setuptools.setup(
    name="productsup_py",
    version="0.0.1",
    url="https://github.com/lyestarzalt/ProductsUp_py",
    author="Lyes Tarzalt",
    author_email="lyestarzalt@gmail.com",
    description="A Python wrapper for the ProductsUp API",
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    install_requires=[
            "requests",
    ],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
