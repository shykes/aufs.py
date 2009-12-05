from distutils.core import setup

setup(name='aufs',
      version='0.0.1',
      author='Solomon Hykes <solomon.hykes@dotcloud.com>',
      package_dir = {
          'aufs' : '.',
          },
      packages=[
          'aufs'
          ]
)
