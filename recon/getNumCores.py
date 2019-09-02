import psutil
import click

@click.command()
@click.option("--maxCores", default=0, help='use to set a maximum number of cores to report.')
def getNumCores(maxcores):
    """ Driver program to return max number of physical cores """

    physNumCores = psutil.cpu_count(logical = False)
    if maxcores != 0:
        if maxcores < physNumCores:
            physNumCores = maxcores

    print(physNumCores, end='')

if __name__ == '__main__':
    getNumCores()