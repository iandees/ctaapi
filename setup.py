from distutils.core import setup

setup(
    name='ctaapi',
    version='0.1',
    author='Ian Dees',
    author_email='ian.dees@gmail.com',
    packages=['ctaapi'],
    url='http://github.com/iandees/ctaapi',
    license='LICENSE',
    description='Wrapper for the CTA API.',
    long_description=open('README.md').read(),
    install_requires=[
        'requests==1.2.3'
    ]
)

