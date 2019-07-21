#!/usr/bin/env nextflow


/*
 * Default pipeline parameters. They can be overriden on the command line eg.
 * given `params.foo` specify on the run command line `--foo some_value`.
 */
params.workingDir = "$HOME/project"
params.subjectID = "DefaultSubject"
params.senFieldMap = "senFM.dat"
params.DWIData = "DWI.dat"

params.protonHome = "/opt/proton/"
params.matlabLicense = "1711@matlab.webstore.illinois.edu"
params.outDir = "$PWD"

senFMDatFile = file(params.senFieldMap)
dwiDatFile = file(params.DWIData)
subjectID = Channel.value(params.subjectID)

//    file PGSE_Siemens_twix_dat from datFiles


process reconSenFM {
// Work around issue with matlab crashing on checking license in.
    validExitStatus 0,137

    container = "mrfil/matlab-recon:r2018b-v5.0.10"
    containerOptions = matlabContainerOpts
    stageInMode = 'copy'

    input:
    file senFM_Siemens_twix_dat from senFMDatFile
    
    output: 
    file 'senFM.mat' into calibrationData

    shell:
    """
    matlab -nodisplay -nodesktop -r "run('${params.protonHome}/initializePaths.m'); reconSenFM_Nextflow('!{senFM_Siemens_twix_dat}');"
    """
}


process prepMultibandDWI_SelfNavigated {

    module "matlab/R2017b"
    cpus 6

    input: 
    file dwi_Siemens_twix_dat from dwiDatFile
    val subjID from subjectID
    file senFM from calibrationData

    output: 
    file 'Shot*.h5' into ISMRMRDFiles

    shell:
    """
    matlab -nodisplay -nodesktop -r "run('${params.protonHome}/initializePaths.m'); prepMultibandDWI_SelfNavigated_Nextflow('!{senFM}','!{dwi_Siemens_twix_dat}','${subjID}');"
    """

}

process runPGReconNavigators {

    container = "mrfil/powergrid"
    containerOptions = "--runtime=nvidia "
	maxForks = 1

    input:
    val subjID from subjectID
    each file(prepFile) from ISMRMRDFiles.flatten()
    
    output: 
    file 'img_Slice*_Rep*_Avg*_Echo*_Phase*_mag.nii' into MagNIIs
    file 'img_Slice*_Rep*_Avg*_Echo*_Phase*_phs.nii' into PhaseNIIs

    shell:
    """
	export OMP_NUM_THREADS=2;
    export OMP_STACKSIZE=32M;
    /opt/PowerGrid/bin/PowerGridIsmrmrd -i !{prepFile} -I hanning -t 0 -F DFT -n 30 -s 1 -D 2 -B100 -o ./
    """

}
/*
process collectPGOutputsShots {
	
    module "matlab/R2017b"

	input:
	
	output:
	file 'img.mat' into Images

	shell:
	"""
	matlab -nodisplay -nodesktop -r "run('/shared/mrfil-data/acerja2/repos/test/startup.m');"
	"""

}

*/


/*
process runPGRecon {
    container = "acerja2/privatepg"
    containerOptions = "--runtime=nvidia "


    input:
    val subjID from subjectID
    file prepFile from ISMRMRDFiles
    
    output: 
    file 'pcSENSE_Slice*_Rep*_Avg*_Echo*_Phase*_mag.nii' into MagNIIs
    file 'pcSENSE_Slice*_Rep*_Avg*_Echo*_Phase*_phs.nii' into PhaseNIIs

    shell:
    """
    /opt/PowerGrid/bin/PowerGridPcSense -i !{prepFile} -x 120 -y 120 -z 4 -n 20 -s 2 -D2 -B 1000 -o ./
    """

}

*/
