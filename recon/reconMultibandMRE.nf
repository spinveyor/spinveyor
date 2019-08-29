#!/usr/bin/env nextflow


/*
 * Default pipeline parameters. They can be overriden on the command line eg.
 * given `params.subjectID` specify on the run command line `--subjectID CIVIC001`.
 */
params.subjectID = "DefaultSubject"
params.senfm = "senFM.dat"
params.imgData = "MRE.dat"

// If you use "", you can do string interpolation ala shell scripting
params.protonHome = "/opt/proton/"
params.matlabLicense = "1711@matlab.webstore.illinois.edu"
params.outDir = "$PWD"

// These lines create channels, which are like super variables with the properites of queues of cells in matlab.
senFMDatFile = file(params.senfm)
mreDatFile = file(params.imgData)
matlabLicense = Channel.value(params.matlabLicense)

// Ancilliary variables
matlabContainerOpts = "-e MLM_LICENSE_FILE=${params.matlabLicense} --shm-size=512M --group-add 61278 --group-add 62046 -v ${params.protonHome}:${params.protonHome}"

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
    file mre_Siemens_twix_dat from mreDatFile
    file senFM from calibrationData

    output: 
    file "${params.subjectID}.h5" into ISMRMRDFiles

    script:
    """
    matlab -nodisplay -nodesktop -r "run('${params.protonHome}/initializePaths.m'); prepMultibandMRE_Nextflow('${senFM}','${mre_Siemens_twix_dat}','${params.subjectID}');"
    """

}

process getNumCores {    

    output: 
    stdout into numCores

    script:
    """
    python3 getNumCores.py
    """
}

process runPGRecon {
    validExitStatus 0,11,139
    
    container = "mrfil/powergrid"
    containerOptions = "--gpus all "


    input:
    file prepFile from ISMRMRDFiles
    val cores from numCores
    output: 
    file 'img_Slice*_Rep*_Avg*_Echo*_Phase*_mag.nii' into MagNIIs
    file 'img_Slice*_Rep*_Avg*_Echo*_Phase*_phs.nii' into PhaseNIIs

    shell:
    """
    mpirun --allow-run-as-root -n !{cores} /opt/PowerGrid/bin/PowerGridPcSenseMPI_TS -i !{prepFile} -n 30 -D2 -B 1000 -o ./
    """

}

process collectPGOutput {
    
    container = "mrfil/matlab-recon:r2018b-v5.0.10"
    containerOptions = matlabContainerOpts
    publishDir = "${params.outDir}/${params.subjectID}"
    input:
    //val subjID from subjectID
    file magNII from MagNIIs
    file phaseNII from PhaseNIIs

    output:
    file 'img.mat' into MREImages

    script:
    """
    matlab -nodisplay -nodesktop -r "run('${params.protonHome}/initializePaths.m'); img = collectPowerGridImgOutput(); save img.mat img;"
    """

}

process preprocessMREData {
    container = "mrfil/matlab-recon:r2018b-v5.0.10"
    containerOptions = matlabContainerOpts
    publishDir = "${params.outDir}/${params.subjectID}"
    input:
    file imgMat from MREImages

    output:
    file 'mr_disp.mat'

    script:
    """
    matlab -nodisplay -nodesktop -r "run('${params.protonHome}/initializePaths.m'); load img.mat; proc_mbmre_bet(img);"
    """
}