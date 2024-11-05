from setuptools import setup, find_packages

setup(
    name='edgegrid-python',
    version='1.3.1',
    description='{OPEN} client authentication protocol for python-requests',
    url='https://github.com/akamai/AkamaiOPEN-edgegrid-python',
    namespace_packages=['akamai'],
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        'requests>=2.24.0',
        'requests_toolbelt>=0.9.1',
        'pyOpenSSL>=19.1.0',
        'ndg-httpsclient>=0.5.1',
        'pyasn1>=0.4.8',
        'urllib3>=1.25.10'
    ],
    extras_require={
        'dev': [
            'pylint>=2.7.0',
            'pytest>=6.1.0',
            'pytest-cov>=2.12.1'
        ],
    },
    include_package_data=True,
    license='Apache 2.0',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ]
)
