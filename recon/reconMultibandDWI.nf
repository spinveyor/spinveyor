#!/usr/bin/env nextflow


/*
 * Default pipeline parameters. They can be overriden on the command line eg.
 * given `params.subjectID` specify on the run command line `--subjectID CIVIC001`.
 */
params.subjectID = "DefaultSubject"
params.senFieldMap = "senFM.dat"
params.DWIData = "DWI.dat"

// If you use "", you can do string interpolation ala shell scripting
params.protonHome = "/opt/proton/"
params.matlabLicense = "1711@matlab.webstore.illinois.edu"
params.outDir = "$PWD"

// These lines create channels, which are like super variables with the properites of queues of cells in matlab.
senFMDatFile = file(params.senFieldMap)
dwiDatFile = file(params.DWIData)
subjectID = Channel.value(params.subjectID)
matlabLicense = Channel.value(params.matlabLicense)

// Ancilliary variables
matlabContainerOpts = "-e MLM_LICENSE_FILE=${params.matlabLicense} --shm-size=512M --group-add 61278 --group-add 62046 -v ${params.SpinVeyorHome}:${params.SpinVeyorHome}"

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

    script:
    """
    matlab -nodisplay -nodesktop -r "run('${params.protonHome}/initializePaths.m'); reconSenFM_Nextflow('${senFM_Siemens_twix_dat}');"
    """
}

process prepMultibandMRE {

    container = "mrfil/matlab-recon:r2018b-v5.0.10"
    containerOptions = matlabContainerOpts

    input: 
    file dwi_Siemens_twix_dat from dwiDatFile
    val subjID from subjectID
    file senFM from calibrationData

    output: 
    file "${subjID}.h5" into ISMRMRDFiles

    script:
    """
    matlab -nodisplay -nodesktop -r "run('${params.SpinVeyorHome}/initializePaths.m'); prepMultibandDWI_Nextflow('${senFM}','${dwi_Siemens_twix_dat}','${subjID}');"
    """

}

process runPGRecon {
    container = "mrfil/powergrid:v1.1.3"
    containerOptions = "--gpus all "


    input:
    file prepFile from ISMRMRDFiles
    
    output: 
    file 'img_Slice*_Rep*_Avg*_Echo*_Phase*_mag.nii' into MagNIIs
    file 'img_Slice*_Rep*_Avg*_Echo*_Phase*_phs.nii' into PhaseNIIs

    shell:
    """
    mpirun --allow-run-as-root -n 6 /opt/PowerGrid/bin/PowerGridPcSenseMPI_TS -i ${prepFile} -n 30 -D2 -B 1000 -o ./
    """

}

process collectPGOutput {
    
    container = "mrfil/matlab-recon:r2018b-v5.0.10"
    containerOptions = matlabContainerOpts
    publishDir = "${params.outDir}/${params.subjectID}"
    input:
    val subjID from subjectID
    file magNII from MagNIIs
    file phaseNII from PhaseNIIs

    output:
    file 'img.mat'

    script:
    """
    matlab -nodisplay -nodesktop -r "run('${params.protonHome}/initializePaths.m'); img = collectPowerGridImgOutput(); save img.mat img;"
    """

}