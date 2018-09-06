"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from __future__ import print_function

import sys
import os
import configparser
import subprocess
import tempdir

from utils import logger

try:
    if hasattr(sys, '_run_from_cmdl') is True:
        raise ImportError
    from pycompss.api.parameter import FILE_IN, FILE_OUT
    from pycompss.api.task import task
    from pycompss.api.api import compss_wait_on
except ImportError:
    logger.warn("[Warning] Cannot import \"pycompss\" API packages.")
    logger.warn("          Using mock decorators.")

    from utils.dummy_pycompss import FILE_IN, FILE_OUT # pylint: disable=ungrouped-imports
    from utils.dummy_pycompss import task # pylint: disable=ungrouped-imports
    from utils.dummy_pycompss import compss_wait_on # pylint: disable=ungrouped-imports

from basic_modules.tool import Tool
from basic_modules.metadata import Metadata

# ------------------------------------------------------------------------------

class TCGA_CD(Tool):
    """
    Tool for writing to a file
    """

    def __init__(self, configuration=None):
        """
        Init function
        """
        logger.info("Test writer")
        Tool.__init__(self)

        local_config = configparser.configparser()
        local_config.read(sys.argv[0] + '.ini')
        self.docker_tag = local_config.get('tcga_cd','docker_tag','latest')
	
	
        if configuration is None:
            configuration = {}

        self.configuration.update(configuration)

    @task(returns=bool, genes_loc=FILE_IN, metrics_ref_dir_loc=FILE_IN, assess_dir_loc=FILE_IN, public_ref_dir_loc=FILE_IN, file_out_loc=FILE_OUT, isModifier=False)
    def validate_and_assess(self, genes_loc, metrics_ref_dir_loc, assess_dir_loc, public_ref_dir_loc, file_out_loc):  # pylint: disable=no-self-use
        participant_id = self.configuration['participant_id']
        cancer_types = self.configuration['cancer_type']
        
        inputDir = os.path.dirname(genes_loc)
        inputBasename = os.path.basename(genes_loc)
        tag = self.docker_tag
        uid = os.getuid()
        
        retval_stage = 'validation'
        retval = subprocess.call([
		"docker","run","--rm","-u", uid,
		'-v',inputDir + ":/app/input:ro",
		'-v',public_ref_dir_loc+":/app/ref:ro",
		"tcga_validation:" + tag,
		'-i',"/app/input/"+inputBasename,'-r','/app/ref/'
	])
	
	if retval == 0:
		retval_stage = 'metrics'
		resultsDir = tempdir.mkdtemp()
		metrics_params = [
			"docker","run","--rm","-u", uid,
			'-v',inputDir + ":/app/input:ro",
			'-v',metrics_ref_dir_loc+":/app/metrics:ro",
			'-v',resultsDir+":/app/results:rw",
			"tcga_metrics:" + tag,
			'-i',"/app/input/"+inputBasename,'-m','/app/metrics/','-p',participant_id,'-o','/app/results/',
			'-c'
		]
		metrics_params.extend(cancer_types)
		
		metrics_retval = subprocess.call(metrics_params)
		if metrics_retval == 0:
			retval_stage = 'assessment'
			assessment_retval = subprocess.call([
				"docker","run","--rm","-u", uid,
				'-v',assess_dir_loc+":/app/assess:ro",
				'-v',resultsDir+":/app/results:rw",
				"tcga_assessment:" + tag,
				'-b',"/app/assess/",'-p','/app/results/','-o','/app/results/'
			])
	
        try:
            if retval == 0:
                putative_goldenFiles = list(map(lambda g: os.path.join(gold_dir_loc,g), os.listdir(gold_dir_loc)))
                goldenFiles = []
                for infile in putative_goldenFiles:
                    if not os.path.isfile(infile):
                        logger.info("ERROR: Check Golden Reference File '%s'" % (infile))
                        continue
                    goldenFiles.append(infile)
                metrics(file_in_loc,ref_dir_loc,species,goldenFiles,file_out_loc)
            else:
                logger.fatal(retval_stage)
        except IOError as error:
            logger.fatal("I/O error({0}): {1}".format(error.errno, error.strerror))
            return False

        return True

    def run(self, input_files, input_metadata, output_files):
        """
        The main function to run the compute_metrics tool

        Parameters
        ----------
        input_files : dict
            List of input files - In this case there are no input files required
        input_metadata: dict
            Matching metadata for each of the files, plus any additional data
        output_files : dict
            List of the output files that are to be generated

        Returns
        -------
        output_files : dict
            List of files with a single entry.
        output_metadata : dict
            List of matching metadata for the returned files
        """

        results = self.validate_and_assess(
            input_files["genes"],
            input_files['metrics_ref_datasets'],
            input_files['assessment_datasets'],
            input_files['public_ref'],
            output_files["metrics"]
        )
        results = compss_wait_on(results)

        if results is False:
            logger.fatal("Test Writer: run failed")
            return {}, {}

        output_metadata = {
            "metrics": Metadata(
		# These ones are already known by the platform
		# so comment them by now
                data_type="metrics",
                file_type="TXT",
                #file_path=output_files["metrics"],
                # Reference and golden data set paths should also be here
                sources=[input_metadata["data"].file_path],
                taxon_id=input_metadata["data"].taxon_id,
                meta_data={
                    "tool": "H_randomizer"
                }
            )
        }

        return (output_files, output_metadata)
