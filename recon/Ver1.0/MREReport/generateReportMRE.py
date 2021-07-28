import click
import os
import shutil
import scipy.io as sio
from skimage.util import montage
import numpy as np
from scipy import ndimage as ndi
import matplotlib.pyplot as plt

# For Report Generation to PDF
import jinja2
import datetime
import pdfkit

@click.command()
@click.argument('matfile', type=click.Path(exists=True))
@click.argument('outputfile', type=click.Path())

def generateReportMRE(matfile, outputfile):

    generateT2StackImage(matfile)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    shutil.copyfile(os.path.join(dir_path,'Illinois-Wordmark-Vertical-Full-Color-RGB.png'),os.path.join(os.getcwd(),'Illinois-Wordmark-Vertical-Full-Color-RGB.png'))
    mat_contents_squeezed = sio.loadmat(matfile,struct_as_record=False, squeeze_me=True)
    mreParams = mat_contents_squeezed['mreParams']
    templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(os.path.abspath(__file__)))
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "mreReportTemplate.j2"
    template = templateEnv.get_template(TEMPLATE_FILE)
    outputText = template.render(matrix_x=mreParams.nx, matrix_y=mreParams.ny, matrix_z=mreParams.nz, fov_x=mreParams.FOVx, fov_y=mreParams.FOVy, fov_z=mreParams.FOVz, oss_snr=round(mreParams.oss_snr,2), current_date_time=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    htmlFilename = os.path.join(os.getcwd(),'mreReport.html')
    html_file = open(htmlFilename, 'w')
    html_file.write(outputText)
    html_file.close()

    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'quiet': '',
        'enable-local-file-access': ''
    }

    pdfkit.from_file(htmlFilename, outputfile, options=options)

def generateT2StackImage(matfile):
    mat_contents = sio.loadmat(matfile)
    t2stack = mat_contents['t2stack']
    
    t2stack = np.rot90(t2stack,2)
    t2stack_montage = montage(np.transpose(t2stack,(2,1,0)), rescale_intensity=True)

    F = plt.figure(figsize = (6, 6))
    plt.imshow(t2stack_montage, cmap=plt.cm.gray)
    plt.gca().axes.get_yaxis().set_visible(False)
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.margins(0,0)
    plt.savefig(os.path.join(os.getcwd(),'t2stack.png'), dpi=150, bbox_inches='tight')


if __name__ == '__main__':
    generateReportMRE()