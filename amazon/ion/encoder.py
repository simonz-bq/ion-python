# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at:
#
#    http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the
# License.

from .core import IonType
from .simple_types import IonPyList, IonPyDict, IonPyNull, IonPyBool, IonPyInt, IonPyFloat, IonPyDecimal, \
    IonPyTimestamp, IonPyText, IonPyBytes, IonPySymbol
from base64 import standard_b64encode
from jsonconversion.encoder import JSONExtendedEncoder


class IonEncoder(JSONExtendedEncoder):

    def isinstance(self, obj, cls):
        if isinstance(obj, (IonPyList, IonPyNull, IonPyBool, IonPyInt, IonPyFloat, IonPyDecimal,
                            IonPyTimestamp, IonPyText, IonPyBytes, IonPySymbol)):
            return False
        return isinstance(obj, cls)

    def default(self, o):
        if (isinstance(o, IonPyInt) or isinstance(o, IonPyBool)) and o.ion_type == IonType.BOOL:
            # Convert BOOL to JSON True/False
            return True if o == 1 else False
        elif isinstance(o, IonPyInt) and o.ion_type == IonType.INT:
            # Arbitrary precision integers are printed as JSON number with precision preserved
            return int(o)
        elif isinstance(o, IonPyList) and (o.ion_type == IonType.LIST or o.ion_type == IonType.SEXP):
            # Lists are printed as JSON array
            # S-expressions are printed as JSON array
            return list(map(self.default, o))
        elif isinstance(o, IonPyDict) and o.ion_type == IonType.STRUCT:
            return {key: self.default(o[key]) for key in o.keys()}
        elif isinstance(o, IonPyNull):
            return None
        elif isinstance(o, IonPyBytes) and o.ion_type == IonType.BLOB:
            return standard_b64encode(o).decode("utf-8")
        elif isinstance(o, IonPyBytes) and o.ion_type == IonType.CLOB:
            return o.decode("utf-8")
        elif isinstance(o, IonPyDecimal) and o.ion_type == IonType.DECIMAL:
            return float(o)
        elif isinstance(o, IonPySymbol) and o.ion_type == IonType.SYMBOL:
            return o.text
        elif isinstance(o, IonPyTimestamp) and o.ion_type == IonType.TIMESTAMP:
            return str(o)
        elif isinstance(o, IonPyText) and o.ion_type == IonType.STRING:
            return str(o)
        elif isinstance(o, IonPyFloat) and o.ion_type == IonType.FLOAT:
            # Floats are printed as JSON number with nan and +-inf converted to JSON null
            if "inf" in str(o) or "nan" in str(o):
                return None
            return float(o)
        else:
            super().default(o)
