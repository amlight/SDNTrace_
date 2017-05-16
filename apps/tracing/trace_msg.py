"""
    
"""


import ast
from datetime import datetime


class TraceMsg(object):
    """
        This class will be used to create, retrieve and update the
        payload message sent through the trace process

        Basically the msg is a dictionary:

        {"trace": {
                "request_id": "number to identify this trace",
                "local_domain" : "name of the local domain",
                "type": "trace type. Possible values: intra|inter",
                "timestamp": "used to track time",
                "inter_path": "if privacy is not an issue, this is an array
                        to identify all domains in the path. Each item
                        of the array is a dictionary:
                            {"domain":{"request_id": 'value',
                                       "timestamp": 'value'}
                            }
                        User doesn't add the timestamp
                        The first item ([0]) is the source domain.
                        if privacy is an issue, this array is empty"
            }
        }
    """

    NOT_PROVIDED = 0

    def __init__(self, r_id='0', r_domain='local', r_type='intra', r_time=0, r_path=0):
        self._request_id = None
        self._local_domain = None
        self._type = None
        self._timestamp = None
        self._inter_path = []

        self._instantiate_vars(r_id, r_domain, r_type, r_time, r_path)

    def _instantiate_vars(self, r_id, r_domain, r_type, r_time, r_path):
        self.request_id = r_id
        self.local_domain = r_domain
        self.type = r_type
        self.timestamp = r_time
        self.inter_path = r_path

    @property
    def id(self):
        return self.request_id

    @property
    def request_id(self):
        return self._request_id

    @request_id.setter
    def request_id(self, r_id):
        try:
            if isinstance(r_id, int):
                self._request_id = r_id
            else:
                self._request_id = int(r_id)
        except ValueError:
            raise ValueError("Invalid ID provided: %s" % r_id)

    @property
    def local_domain(self):
        return self._local_domain

    @local_domain.setter
    def local_domain(self, r_domain):
        try:
            if len(r_domain) > 0:
                self._local_domain = r_domain
        except ValueError:
            raise ValueError("Invalid Domain provided: %s" % r_domain)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, r_type):
        try:
            if isinstance(r_type, str) and r_type in ['intra', 'inter']:
                self._type = r_type
            else:
                raise ValueError
        except ValueError:
            raise ValueError("Invalid Type provided: %s" % r_type)

    @property
    def timestamp(self):
        return self._timestamp

    def get_timestamp(self, label=None):
        if not label:
            return self.timestamp
        elif label == 'str':
            return str(self.timestamp)
        elif label == 'timestamp':
            return int(self.timestamp.strftime("%s"))

    @timestamp.setter
    def timestamp(self, r_timestamp=None):
        try:
            if r_timestamp is not self.NOT_PROVIDED:
                if isinstance(r_timestamp, str):
                    time_format = '%Y-%m-%d %H:%M:%S.%f'
                    r_timestamp = datetime.strptime(r_timestamp, time_format)
                    self._timestamp = r_timestamp
                else:
                    raise ValueError
            else:
                self._timestamp = datetime.now()
        except ValueError:
            raise ValueError("Invalid Timestamp provided: %s" % r_timestamp)

    @property
    def inter_path(self):
        return self._inter_path

    @inter_path.setter
    def inter_path(self, r_inter_path):
        """
            Set the self.inter_path variable
            if a list or a dict is provided, append to the end of the current list
            if nothing is provided, delete the current value
            Args:
                r_inter_path: a list or a dict of paths
        """
        try:
            if self.type == 'intra':
                if self.local_domain == 'local':
                    r_inter_path = {self.local_domain: str(self.request_id)}
                check_domain = False
            else:
                check_domain = self.local_domain

            if isinstance(r_inter_path, list) and len(r_inter_path) > 0:
                for domain in r_inter_path:
                    path = Path(domain, check_domain)
                    self._inter_path.append(path.path)
            elif isinstance(r_inter_path, dict):
                path = Path(r_inter_path, check_domain)
                self._inter_path.append(path.path)
            elif r_inter_path is 0 or isinstance(r_inter_path, list):
                self._inter_path = []
            else:
                print('Error: inter_trace else')
                raise ValueError
        except ValueError:
            raise ValueError("Invalid Path provided: %s" % r_inter_path)

    def import_data(self, entries):
        """
            Import data from a dictionary with format similar to self.data
            Args:
                entries: dictionary of exported data from self.data
        """
        if isinstance(entries, str):
            entries = ast.literal_eval(entries)
        r_id = entries['request_id']
        r_domain = entries['local_domain']
        r_type = entries['type']
        r_time = entries['timestamp']
        self._inter_path = []
        r_path = entries['inter_path']
        self._instantiate_vars(r_id, r_domain, r_type, r_time, r_path)

    def data(self):
        result = dict()
        result['request_id'] = self.request_id
        result['local_domain'] = self.local_domain
        result['type'] = self.type
        result['timestamp'] = self.get_timestamp(label='str')
        for domain in self.inter_path:
            key = domain.keys()[0]
            domain[key]['timestamp'] = str(domain[key]['timestamp'])
        result['inter_path'] = self.inter_path
        return result

    def __str__(self):
        return str(self.data())

    def get_last_id(self):
        domain_name = self.inter_path[-1].keys()[0]
        return self.inter_path[-1][domain_name]['request_id']

    def set_interdomain(self):
        """
            A probe trace will be sent. Prepare payload
        """
        self.inter_path = {self.local_domain: {'request_id': self.request_id,
                                               'timestamp': self.get_timestamp(label='str')}}
        self.type = 'inter'


class Path(object):
    """
        This class is used just to validate the inter_path from
        class TraceMsg
        It is not instantiate by any other class
    """
    def __init__(self, domain, compare_domain=False):
        self._path = None
        self.compare_domain = compare_domain
        self.instantiate_vars(domain)

    def instantiate_vars(self, domain):
        self.path = domain

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, domain):
        if self.is_valid_domain(domain):
            keys = domain.keys()[0]
            values = domain.values()[0]
            domain[keys] = self.add_time(values)
            self._path = domain
        else:
            print('Path.setter not possible')
            raise ValueError

    def is_valid_domain(self, domain):
        """
            Look for a single {'name':'number'}
            Args:
                domain: expected to be a dict with {'name':'number'}
            Returns:
                True: correct path format
                False: incorrect path format
        """
        if isinstance(domain, dict):
            if len(domain) == 1:
                if self.compare_domain is False:
                    # It means it is an intra test, ignore
                    if isinstance(domain.values()[0], str):
                        return True
                    elif isinstance(domain.values()[0], dict):
                        return True
                elif self.is_local_and_remote_equal(domain):
                    print('Error: local_domain and path can not be the same')
                    return False
                else:
                    if isinstance(domain.values()[0], str):
                        return True
                    elif isinstance(domain.values()[0], dict):
                        return True
        return False

    def is_local_and_remote_equal(self, domain):
        if domain.keys()[0] is self.compare_domain:
            return True
        return False

    @staticmethod
    def add_time(values):
        """
            Convert the "request_id number" in {'name':'number'}
            to a new dict with timestamp. Final result:
            {'request_id': 'number', 'timestamp': datetime.now()}}
            Args:
                values: the request_id number
            Returns:
                dictionary
        """
        new_values = dict()
        if isinstance(values, dict):
            # If imported
            new_values['request_id'] = values['request_id']
            new_values['timestamp'] = values['timestamp']
        else:
            # If brand new
            new_values['request_id'] = values
            new_values['timestamp'] = datetime.now()
        return new_values
