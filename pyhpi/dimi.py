# Copyright (c) 2014  Kontron Europe GmbH
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import datetime
import array

from sahpi import *
from utils import TextBuffer, BaseHpiObject
from errors import EncodingError

class DimiInfo(BaseHpiObject):
    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)
        self.num_tests = s.NumberOfTests
        self.update_counter = s.TestNumUpdateCounter

        return self

class DimiTestParameterDefinition(BaseHpiObject):
    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)
        self.name = array.array('B', s.ParamName).tostring().rstrip('\x00')
        self.info = TextBuffer().from_ctype(s.ParamInfo)
        self.type = s.ParamType.value

        self.min = None
        self.max = None
        if self.type == SAHPI_DIMITEST_PARAM_TYPE_BOOLEAN:
            self.default = bool(s.DefaultParam.parambool)
        elif self.type == SAHPI_DIMITEST_PARAM_TYPE_INT32:
            self.min = int(s.MinValue.IntValue)
            self.max = int(s.MaxValue.IntValue)
            self.default = int(s.DefaultParam.paramint)
        elif self.type == SAHPI_DIMITEST_PARAM_TYPE_FLOAT64:
            self.min = int(s.MinValue.FloatValue)
            self.max = int(s.MaxValue.FloatValue)
            self.default = float(s.DefaultParam.paramfloat)
        elif self.type == SAHPI_DIMITEST_PARAM_TYPE_TEXT:
            self.default = TextBuffer().from_ctype(s.DefaultParam.paramtext)
        else:
            raise DecodingError("Unknown DIMI test parameter type %d" %
                    self.type)

        return self


class DimiTestParameter(BaseHpiObject):
    def __init__(self, name=None, value=None):
        if name is not None:
            self.name = name
        if value is not None:
            self.value = value
            # order matters!
            if isinstance(value, float):
                self.type = SAHPI_DIMITEST_PARAM_TYPE_BOOLEAN
            elif isinstance(value, bool):
                self.type = SAHPI_DIMITEST_PARAM_TYPE_FLOAT64
            elif isinstance(value, basestring):
                self.type = SAHPI_DIMITEST_PARAM_TYPE_TEXT
            elif isinstance(value, int):
                self.type = SAHPI_DIMITEST_PARAM_TYPE_INT32
            else:
                raise ValueError('unknown type: %s', type(param))

    def to_ctype(self):
        if len(self.name) > 20:
            raise EncodingError('parameter name too long')
        t = SaHpiDimiTestVariableParamsT()
        t.ParamName[:len(self.name)] = \
                array.array('B', str(self.name)).tolist()
        t.ParamType = self.type
        if self.type == SAHPI_DIMITEST_PARAM_TYPE_BOOLEAN:
            t.Value.parambool = SaHpiBoolT(self.value)
        elif self.type == SAHPI_DIMITEST_PARAM_TYPE_INT32:
            t.Value.paramint = SaHpiInt32T(self.value)
        elif self.type == SAHPI_DIMITEST_PARAM_TYPE_FLOAT64:
            t.Value.paramfloat = SaHpiFloat64T(self.value)
        elif self.type == SAHPI_DIMITEST_PARAM_TYPE_TEXT:
            t.Value.paramtext = TextBuffer(self.value).to_ctype()

        return t


class DimiResults(BaseHpiObject):
    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)

        self.timestamp = \
            datetime.datetime.fromtimestamp(s.ResultTimeStamp/1000000000)
        self.run_duration = \
            datetime.timedelta(microseconds=s.RunDuration/1000)
        self.last_run_status = s.LastRunStatus.value
        self.error_code = s.TestErrorCode.value
        self.result = TextBuffer().from_ctype(s.TestResultString)

        return self


class DimiTest(BaseHpiObject):
    def __init__(self, session, resource, dimi, test_num):
        self.session = session
        self.resource = resource
        self.dimi = dimi
        self._as_parameter_ = SaHpiDimiTestNumT(test_num)

    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)

        self.name = TextBuffer().from_ctype(s.TestName)
        self.service_impact = s.ServiceImpact.value
        #self.impacted_entities = s.EntitiesImpacted
        self.service_os_needed = bool(s.NeedServiceOS)
        self.expected_run_duration = \
                datetime.timedelta(microseconds=s.ExpectedRunDuration/1000)
        self.capabilities = s.TestCapabilities
        self.parameters = list()
        for param in s.TestParameters:
            # design flaw: there is no indication how many parameters are in
            # use.
            if param.ParamName[0] == 0:
                break
            self.parameters.append(DimiTestParameterDefinition().from_ctype(param))

        return self

    def is_ready(self):
        """Queries the test 'readiness'."""
        ready = SaHpiDimiReadyT()
        saHpiDimiTestReadinessGet(self.session, self.resource, self.dimi, self,
                byref(ready))
        return ready

    def cancel(self):
        saHpiDimiTestCancel(self.session, self.resource, self.dimi, self)

    def start(self, parameters=None):
        """Starts a DIMI test."""
        if parameters is not None:
            _params = [DimiTestParameter(*p) for p in parameters]
            params = (SaHpiDimiTestVariableParamsT * len(_params))()
            for i in xrange(len(_params)):
                params[i] = _params[i].to_ctype()
            num_params = len(params)
        else:
            params = None
            num_params = 0
        saHpiDimiTestStart(self.session, self.resource, self.dimi, self,
                num_params, params)

    def status(self):
        """Queries the test status and returns the tuple (status, percent)."""
        percent = SaHpiDimiTestPercentCompletedT()
        status = SaHpiDimiTestRunStatusT(0)
        saHpiDimiTestStatusGet(self.session, self.resource, self.dimi, self,
                byref(percent), byref(status))

        percent = int(percent.value)
        if percent == 0xff:
            percent = None

        return status.value, percent

    def results(self):
        """Queries the result of a dimi test."""
        results = SaHpiDimiTestResultsT()
        saHpiDimiTestResultsGet(self.session, self.resource, self.dimi, self,
                byref(results))

        return DimiResults().from_ctype(results)


class Dimi(object):
    def __init__(self, session, resource, dimi_num):
        self.session = session
        self.resource = resource
        self._as_parameter_ = SaHpiDimiNumT(dimi_num)
        self._test_list = None
        self._last_update_count = 0

    def info(self):
        info = SaHpiDimiInfoT();
        saHpiDimiInfoGet(self.session, self.resource, self, byref(info))
        return DimiInfo().from_ctype(info)

    def _update_test_list(self):
        tests = list()

        retries = 3
        while retries != 0:
            del tests[:]
            info = self.info()
            try:
                for test_no in xrange(info.num_tests):
                    _test = SaHpiDimiTestT()
                    saHpiDimiTestInfoGet(self.session, self.resource, self,
                            test_no, byref(_test))
                    test = DimiTest(self.session, self.resource, self, test_no)
                    test.from_ctype(_test)
                    tests.append(test)
                if info.update_counter == self.info().update_counter:
                    # update counter was not changed, we finished
                    break
            except SaHpiError, e:
                if e.errno == SA_ERR_HPI_NOT_PRESENT:
                    retries -= 1
                    continue
                else:
                    raise

            retries -= 1
        else:
            raise RetriesExceededError()

        self._test_list = tests

    def get_test_by_num(self, test_num):
        return self.test_list()[test_num]

    def test_list(self):
        if (self._test_list is None
                or self._last_update_count < self.info().update_counter):
            self._update_test_list()

        return self._test_list
