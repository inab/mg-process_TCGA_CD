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

from .scripts.validation import validation
from .scripts.metrics import metrics

# ------------------------------------------------------------------------------

class H_randomizer(Tool):
    """
    Tool for writing to a file
    """

    def __init__(self, configuration=None):
        """
        Init function
        """
        logger.info("Test writer")
        Tool.__init__(self)

        if configuration is None:
            configuration = {}

        self.configuration.update(configuration)

    @task(returns=bool, file_in_loc=FILE_IN, file_out_loc=FILE_OUT, isModifier=False)
    def compute_metrics(self, file_in_loc, file_out_loc):  # pylint: disable=no-self-use
        """
        Count the number of characters in a file and return a file with the count

        Parameters
        ----------
        file_in_loc : str
            Location of the input file
        ref_dir_loc : str
            Location of the reference and golden data sets directory
        file_out_loc : str
            Location of an output file

        Returns
        -------
        bool
            Writes the metrics to the file
        """
        ref_dir_loc = self.configuration['reference_data']
        gold_dir_loc = self.configuration['golden_data']
        species = self.configuration['species']
        ok_validation = validation(file_in_loc,ref_dir_loc,species)
        try:
            if ok_validation is True:
                putative_goldenFiles = list(map(lambda g: os.path.join(gold_dir_loc,g), os.listdir(gold_dir_loc)))
                goldenFiles = []
                for infile in putative_goldenFiles:
                    if not os.path.isfile(infile):
                        logger.info("ERROR: Check Golden Reference File '%s'" % (infile))
                        continue
                    goldenFiles.append(infile)
                metrics(file_in_loc,ref_dir_loc,species,goldenFiles,file_out_loc)
            else:
                logger.fatal(ok_validation)
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

        results = self.compute_metrics(
            input_files["data"],
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
