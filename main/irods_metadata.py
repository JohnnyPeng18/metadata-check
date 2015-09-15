"""
Copyright (C) 2015  Genome Research Ltd.

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is part of metadata-check

metadata-check is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

This file has been created on Jun 23, 2015.
"""

import re
import error_types
import metadata_utils
from com import utils as common_utils
from irods import icommands_wrapper, constants as irods_consts


class IrodsSeqFileMetadata(object):

    def __init__(self, fpath=None, fname=None, samples=[], libraries=[], studies=[], md5=None,
                 ichksum_md5=None, reference=None, run_id=None, lane_id=None, npg_qc=None, target=None):
        self.fname = fname
        self.fpath = fpath
        self.samples = samples
        self.libraries = libraries
        self.studies = studies
        self.md5 = md5
        self.ichksum_md5 = ichksum_md5
        self.reference = reference
        self.run_id = run_id
        self.lane_id = lane_id
        self.npg_qc = npg_qc
        self.target = target

    @classmethod
    def from_avus_to_irods_metadata(cls, avus, fpath):
        '''
        :param avus:
        :param fpath:
        :return: an iRODSFileMetadata object
        WARNING: this assumes that a file has metadata as the data objects in seq zone - ie assumes there should be
        exactly 1 md5, 1 lane id, 1 run id, 1 manual_qc field => won't work for more complex metadata schemes
        => ignores avu frequency errors => this should be checked beforehands...somewhere...
        '''
        fname = common_utils.extract_fname(fpath)
        samples = metadata_utils.iRODSiCmdsUtils.extract_samples_from_irods_metadata(avus)
        libraries = metadata_utils.iRODSiCmdsUtils.extract_libraries_from_irods_metadata(avus)
        studies = metadata_utils.iRODSiCmdsUtils.extract_studies_from_irods_metadata(avus)

        md5_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'md5')
        md5 = md5_list[0] if len(md5_list) == 1 else None

        # TODO: actually this is not according to the method's name, it doesn't build up metadata from avus but also queries irods independently
        #ichksum_md5 = icommands_wrapper.iRODSChecksumOperations.get_checksum(fpath)

        ref_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'reference')
        ref = ref_list[0] if len(ref_list) == 1 else None

        # TODO: I don't deal with the exception thrown from extract_reference_name.. if the ref doesn't look like a ref
        if ref:
            ref = cls.extract_reference_name_from_ref_path(ref)

        run_id_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'id_run')
        run_id = run_id_list[0] if len(run_id_list) == 1 else None

        lane_id_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'lane')
        lane_id = lane_id_list[0] if len(lane_id_list) == 1 else None

        npg_qc_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'manual_qc')
        npg_qc = npg_qc_list[0] if len(npg_qc_list) == 1 else None

        target_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'target')
        target = target_list[0] if len(target_list) == 1 else None

        return IrodsSeqFileMetadata(fpath=fpath, fname=fname, samples=samples, libraries=libraries,
                                    studies=studies, md5=md5, reference=ref, run_id=run_id,
                                    lane_id=lane_id, npg_qc=npg_qc, target=target)


    @classmethod
    def run_avu_count_checks(cls, fpath, avus):
        problems = []
        md5_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'md5')
        if len(md5_list) != 1:
            problems.append(error_types.IrodsMetadataAttributeFrequencyError(fpath, 'md5', '1', str(len(md5_list))))

        ref_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'reference')
        if len(ref_list) != 1:
            problems.append(error_types.IrodsMetadataAttributeFrequencyError(fpath, 'reference', '1', str(len(ref_list))))

        run_id_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'id_run')
        if len(run_id_list) != 1:
            problems.append(error_types.IrodsMetadataAttributeFrequencyError(fpath, 'id_run', '1', str(len(run_id_list))))

        lane_id_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'lane')
        if len(lane_id_list) != 1:
            problems.append(error_types.IrodsMetadataAttributeFrequencyError(fpath, 'lane', '1', str(len(lane_id_list))))

        npg_qc_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'manual_qc')
        if len(npg_qc_list) != 1:
            problems.append(error_types.IrodsMetadataAttributeFrequencyError(fpath, 'manual_qc', '1', str(len(npg_qc_list))))
        return problems


#         samples = metadata_utils.iRODSiCmdsUtils.extract_samples_from_irods_metadata(avus)
#         libraries = metadata_utils.iRODSiCmdsUtils.extract_libraries_from_irods_metadata(avus)
#         studies = metadata_utils.iRODSiCmdsUtils.extract_studies_from_irods_metadata(avus)


            # # Filter out non-ids
            # filtered_ids = filter_ids(ids_list)
            # non_ids = set(ids_list).difference(set(filtered_ids))
            # problems.extend([error_types.NotFoundInSeqscapeError(id_type, id, entity_type) for id in non_ids]) # id_type, id_missing, entity_type, fpath=None):

        # irods_samples = {'name': irods_sample_names_list,
        #                  'accession_number': irods_sample_acc_nr_list,
        #                  'internal_id': irods_sample_internal_id_list
        # }

    # @classmethod
    # def _filter_out_non_ids(cls, ids_list):
    #     return [id for id in ids_list if id not in ['N/A', 'undefined', 'unspecified']]
    #
    # # ugly method - these things should be separated (filtering out, reporting errors, and putting together the right error to be returned directly to the user)
    # # plus I silently access the fpath field from this object, dirty!!!
    # def _filter_out_non_entities(self, entity_dict, entity_type):
    #     filtered_entities = {}
    #     problems = []
    #     for id_type, ids_list in entity_dict.items():
    #         filtered_ids = cls._filter_out_non_ids(ids_list)
    #         non_ids = set(ids_list).difference(set(filtered_ids))
    #         problems.extend([error_types.WrongIrodsMetadataValue(fpath=self.fpath, attribute=str(entity_type)+'_'+str(id_type), value=id) for id in non_ids])
    #         filtered_entities[id_type] = filtered_ids
    #     return filtered_entities, problems
    #

    def run_field_sanity_checks_and_filter(self):
        problems = []
        if self.samples:
            #self.samples, pbs = self._filter_out_non_entities(self.samples)
            self.samples, pbs = metadata_utils.GeneralUtils.filter_out_non_entities(self.fpath, self.samples, 'sample')
            pbs = [error_types.WrongIRODSMetadataValue(err.fpath, err.attribute, err.value) for err in pbs]
            problems.extend(pbs)

        if self.libraries:
            self.libraries, pbs = metadata_utils.GeneralUtils.filter_out_non_entities(self.fpath, self.libraries, 'library')
            pbs = [error_types.WrongIRODSMetadataValue(err.fpath, err.attribute, err.value) for err in pbs]
            problems.extend(pbs)

        if self.studies:
            self.studies, pbs = metadata_utils.GeneralUtils.filter_out_non_entities(self.fpath, self.studies, 'study')
            pbs = [error_types.WrongIRODSMetadataValue(err.fpath, err.attribute, err.value) for err in pbs]
            problems.extend(pbs)

        if self.md5 and not self.is_md5(self.md5):
            problems.append(error_types.WrongMetadataValue(fpath=self.fpath, attribute='md5', value=self.md5))
        if self.ichksum_md5 and not self.is_md5(self.ichksum_md5):
            problems.append(error_types.WrongMetadataValue(fpath=self.fpath, attribute='ichcksum_md5', value=self.ichksum_md5))
        if self.run_id and not self.is_run_id(self.run_id):
            problems.append(error_types.WrongMetadataValue(fpath=self.fpath, attribute='run_id', value=self.run_id))
        if self.lane_id and not self.is_lane_id(self.lane_id):
            problems.append(error_types.WrongMetadataValue(fpath=self.fpath, attribute='lane_id', value=self.lane_id))
        if self.npg_qc and not self.is_npg_qc(self.npg_qc):
            problems.append(error_types.WrongMetadataValue(fpath=self.fpath, attribute='npg_qc', value=self.npg_qc))
        if self.target and not self.is_target(self.target):
            problems.append(error_types.WrongMetadataValue(fpath=self.fpath, attribute='target', value=self.target))
        return problems


    @classmethod
    def is_md5(cls, md5):
        if not type(md5) is str:
            raise TypeError("WRONG TYPE: the MD5 must be a string, and is: " + str(type(md5)))
        r = re.compile(irods_consts.MD5_REGEX)
        return True if r.match(md5) else False

    @classmethod
    def is_run_id(cls, run_id):
        if not type(run_id) in [str, int]:
            raise TypeError("WRONG TYPE: the run_id must be a string or int and is: " + str(type(run_id)))
        r = re.compile(irods_consts.RUN_ID_REGEX)
        return True if r.match(str(run_id)) else False

    @classmethod
    def is_lane_id(cls, lane_id):
        if not type(lane_id) in [str, int]:
            raise TypeError("WRONG TYPE: the lane_id must be either string or int and is: " + str(type(lane_id)))
        r = re.compile(irods_consts.LANE_ID_REGEX)
        return True if r.match(str(lane_id)) else False

    @classmethod
    def is_npg_qc(cls, npg_qc):
        if not type(npg_qc) in [str, int]:
            raise TypeError("WRONG TYPE: the npg_qc must be either string or int and is: " + str(npg_qc))
        r = re.compile(irods_consts.NPG_QC_REGEX)
        return True if r.match(str(npg_qc)) else False


    @classmethod
    def is_target(cls, target):
        if not type(target) in [str, int]:
            raise TypeError("WRONG TYPE: the target must be either string or int and is: " + str(target))
        r = re.compile(irods_consts.TARGET_REGEX)
        return True if r.match(str(target)) else False


    @classmethod
    def check_is_irods_seq_fpath(cls, fpath):
        r = re.compile(irods_consts.IRODS_SEQ_LANELET_PATH_REGEX)
        if not r.match(fpath):
            raise ValueError("Not an iRODS seq path: " + str(fpath))


    @classmethod
    def check_is_lanelet_filename(cls, fname):
        """
        Checks if a filename looks like: 1234_5.* or 1234_5#6.*
        :param fname: file name
        :return: bool
        """
        r = re.compile(irods_consts.LANLET_NAME_REGEX)
        if not r.match(fname):
            raise ValueError("Not a lanelet filename: " + str(fname))


    @classmethod
    def check_is_irods_lanelet_fpath(cls, fpath):
        """
        Checks if a given file path is an irods seq path and that it is a lanelet. e.g. 1234_5.bam, 1234_5#6.cram
        :param fpath:
        :return:
        """
        cls.check_is_irods_seq_fpath(fpath)
        fname = common_utils.extract_fname_without_ext(fpath)
        cls.check_is_lanelet_filename(fname)


    @classmethod
    def extract_lanelet_name_from_irods_fpath(cls, irods_fpath):
        """
        This method extracts the lanelet name (without extension) from an irods path.
        It checks first that it is an iRODS seq lanelet.
        :raises ValueError if the irods_path param is not a seq/run_id/lanelet.
        :param irods_fpath:
        :return:
        """
        cls.check_is_irods_lanelet_fpath(irods_fpath)
        fname_without_ext = common_utils.extract_fname_without_ext(irods_fpath)
        return fname_without_ext


    @classmethod
    def get_run_from_irods_path(cls, irods_fpath):
        """
            This function extracts the run_id from the filename of the irods_path given as parameter.
        :param irods_fpath:
        :return:
        :raises: ValueError if the path doesnt look like an irods sequencing path or the file is not a lanelet.
        """
        fname = cls.extract_lanelet_name_from_irods_fpath(irods_fpath)
        return cls.get_run_from_irods_fname(fname)


    @classmethod
    def get_run_from_irods_fname(cls, fname):
        cls.check_is_lanelet_filename(fname)
        r = re.compile(irods_consts.LANLET_NAME_REGEX)
        matched_groups = r.match(fname).groupdict()
        return matched_groups['run_id']


    @classmethod
    def get_lane_from_irods_path(cls, irods_fpath):
        cls.check_is_irods_seq_fpath(irods_fpath)
        fname = common_utils.extract_fname_without_ext(irods_fpath)
        return cls.get_lane_from_irods_fname(fname)


    @classmethod
    def get_lane_from_irods_fname(cls, fname):
        cls.check_is_lanelet_filename(fname)
        r = re.compile(irods_consts.LANLET_NAME_REGEX)
        matched_groups = r.match(fname).groupdict()
        return matched_groups['lane_id']


    @classmethod
    def extract_reference_name_from_ref_path(cls, ref_path):
        ref_file_name = common_utils.extract_fname(ref_path)
        if ref_file_name.find(".fa") != -1:
            ref_name = ref_file_name.split(".fa")[0]
            return ref_name
        else:
            raise ValueError("Not a reference file: " + str(ref_path))



    def test_run_id_from_fname_vs_metadata(self):
        """
        This test assumes that all the files in iRODS have exactly 1 run (=LANELETS)
        """
        if not self.run_id:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath,
                                                       reason='The run_id in iRODS metadata is either missing or more than 1.',
                                                       test_name='Check run_id from filename vs. iRODS metadata.')
        try:
            run_id_from_fname = self.get_run_from_irods_fname(self.fname)
        except ValueError as e:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath, reason=str(e), test_name='Check run_id from filename vs. run_id from iRODS metadata') # 'Cant extract the run id from file name. Not a sequencing file?'
        else:
            if str(self.run_id) != str(run_id_from_fname):
                raise error_types.IrodsMetadataAttributeVsFileNameError(fpath=self.fpath, attribute='run_id', irods_value=self.run_id, filename_value=run_id_from_fname)


    # TODO: actually the user can't know exactly the name of the files - this needs refactoring, in order to associate the name of the ref file with the name of the ref
    def test_reference(self, desired_ref):
        if not self.reference:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath, test_name='Check reference',reason='The reference from iRODS metadata is either missing or more than 1.')
        if not desired_ref:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath, test_name='Check_reference', reason='Missing desired reference parameter.')
        #if self.reference != desired_ref:
        if self.reference.find(desired_ref) == -1:
            raise error_types.WrongReferenceError(fpath=self.fpath, desired_ref=desired_ref, header_ref='not implemented', irods_ref=self.reference)


    def test_md5_calculated_vs_metadata(self):
        if self.ichksum_md5 and self.md5:
            if self.ichksum_md5 != self.md5:
                raise error_types.WrongMD5Error(fpath=self.fpath, imeta_value=self.md5, ichksum_value=self.ichksum_md5)
        else:
            if not self.ichksum_md5:
                raise error_types.TestImpossibleToRunError(fpath=self.fpath, test_name='Test md5', reason='The md5 returned by ichksum is missing')
            if not self.md5:
                raise error_types.TestImpossibleToRunError(fpath=self.fpath, test_name='Test md5', reason='The md5 in iRODS metadata is either missing or more than 1.')


    def test_lane_from_fname_vs_metadata(self):
        if not self.lane_id:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath,
                                                       reason='The lane id in the iRODS metadata is either missing or more than 1 ',
                                                       test_name='Check lane id from filename vs iRODS metadata')
        try:
            lane_from_fname = self.get_lane_from_irods_fname(self.fname)
        except ValueError as e:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath,
                                                       reason=str(e),
                                                       test_name='Check lane id from filename vs iRODS metadata')
        else:
            if str(lane_from_fname) != str(self.lane_id):
                raise error_types.IrodsMetadataAttributeVsFileNameError(fpath=self.fpath, attribute='lane', irods_value=self.lane_id, filename_value=lane_from_fname)


    def __str__(self):
        return "Fpath = " + str(self.fpath) + ", fname = " + str(self.fname) + ", samples = " + str(self.samples) + \
               ", libraries = " + str(self.libraries) + ", studies = " + str(self.studies)

    def __repr__(self):
        return self.__str__()