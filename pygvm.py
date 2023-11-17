from .utils import dict_to_lxml, lxml_to_dict
from .response import Response
from .exceptions import ResultError
from .exceptions import HTTPError
from .exceptions import ElementExists
from .exceptions import ElementNotFound
from .exceptions import InvalidArgumentError
from .exceptions import ServerError
from gvm.protocols.latest import Gmp
from gvm.xml import pretty_print
import six

DEFAULT_SCANNER_NAME = "OpenVAS Default"
DEFAULT_CONFIG_NAME = "Full and fast"
DEFAULT_FORMAT_NAME = "TXT"

class Pygvm:
    def __init__(self, gmp:Gmp, username, passwd):
        self.gmp = gmp
        self.gmp.authenticate(username, passwd)
    
    def _command(self, resp, cb=None) -> Response:
        response = Response(resp=resp, cb=cb)
        # validate response, raise exceptions, if any
        response.raise_for_status()
        return response
    
    def _create(self, resp, cb):
        return self._command(resp=resp, cb=cb)
        
    def _get(self, resp, data_type, cb=None) -> Response:
        if cb is None:
            def cb(resp):
                return list(
                    lxml_to_dict(resp.find(data_type)).values()
                )[0]
        return self._command(resp=resp, cb=cb)
    
    def _list(self, resp, data_type, cb=None) -> Response:
        if cb is None:
            def cb(resp):
                return [lxml_to_dict(i, True) for i in resp.findall(data_type)]
        return self._command(resp=resp, cb=cb)
        
    def get_version(self):
        resp = self.gmp.get_version()
        return self._get(resp=resp, data_type='version')
        
    def list_targets(self):
        resp = self.gmp.get_targets()
        return self._list(resp=resp, data_type='target')
    
    def get_target(self, target_id):
        resp = self.gmp.get_target(target_id=target_id)
        return self._get(resp=resp, data_type='target')
    
    def create_target(self, name, hosts, port_list_id=None, alive_tests=None, comment=None):
        """Creates a target of hosts."""
        resp = self.gmp.create_target(name=name, hosts=hosts, port_list_id=port_list_id, alive_test=alive_tests, comment=comment)
        return self._create(resp=resp)

    def modify_target(self, target_id, name=None, hosts=None, port_list_id=None, alive_tests=None, comment=None):
        resp = self.gmp.modify_target(target_id=target_id, 
                               name=name,
                               hosts=hosts,
                               port_list_id=port_list_id,
                               comment=comment,
                               alive_test=alive_tests)
        return self._command(resp=resp)

    def delete_target(self, target_id):
        """Deletes a target with given id."""
        resp = self.gmp.delete_target(target_id=target_id)
        return self._command(resp=resp)
    
    def list_configs(self):
        resp = self.gmp.get_scan_configs()
        return self._list(resp=resp, data_type='config')
    
    def get_config(self, config_id):
        resp = self.gmp.get_scan_config(config_id=config_id)
        return self._get(resp=resp, data_type='config')
    
    def create_config(self, name, copy_config_id, comment=None):
        """Creates a new config or copies an existing config using the id of a config using copy_uuid."""
        resp = self.gmp.create_scan_config(name=name, config_id=copy_config_id, comment=comment)
        return self._create(resp=resp)
    
    def delete_config(self, config_id):
        resp = self.gmp.delete_scan_config(config_id=config_id)
        return self._command(resp=resp)
    
    def list_port_lists(self, **kwargs):
        """Returns list of port lists, filtering via kwargs"""
        resp = self.gmp.get_port_lists()
        return self._list(resp=resp, data_type="port_list")

    def get_port_list(self, port_list_id):
        """Returns a single port list using an @id"""
        resp = self.gmp.get_port_list(port_list_id=port_list_id)
        return self._get(resp=resp, data_type="port_list")
    
    def create_port_list(self, name, port_range, comment=None):
        """Creates a target of hosts."""
        resp = self.gmp.create_port_list(name=name, port_range=port_range, comment=comment)
        return self._create(resp=resp)
    
    def delete_port_list(self, port_list_id):
        """Creates a target of hosts."""
        resp = self.gmp.delete_port_list(port_list_id=port_list_id)
        return self._command(resp=resp)
    
    def list_scanners(self, **kwargs):
        """List scanners and filter using kwargs."""
        if kwargs is not {}:
            def get_filter_str(k, v):
                return "{}=\"{}\"".format(k, v)
            filter_str = " ".join([get_filter_str(k, v) for k, v in six.iteritems(kwargs) if v])
        resp = self.gmp.get_scanners(filter_string=filter_str)
        return self._list(resp=resp, data_type="scanner")
    
    def get_scanners(self, scanner_id):
        resp = self.gmp.get_scanner(scanner_id=scanner_id)
        return self._get(resp=resp, data_type="scanner") 
    
    def list_report_formats(self, **kwargs):
        """List report formats with kwargs filters."""
        if kwargs is not {}:
            def get_filter_str(k, v):
                return "{}=\"{}\"".format(k, v)
            filter_str = " ".join([get_filter_str(k, v) for k, v in six.iteritems(kwargs) if v])
        resp = self.gmp.get_report_formats(filter_string=filter_str)
        return self._list(resp=resp, data_type="report_format")

    def get_report_format(self, report_format_id):
        """Get report format with uuid."""
        resp = self.gmp.get_report_format(report_format_id=report_format_id)
        return self._get(resp=resp, data_type="report_format")
    
    def list_tasks(self, **kwargs):
        if kwargs is not {}:
            def get_filter_str(k, v):
                return "{}=\"{}\"".format(k, v)
            filter_str = " ".join([get_filter_str(k, v) for k, v in six.iteritems(kwargs) if v])
        resp = self.gmp.get_tasks(filter_string=filter_str)
        return self._list(resp=resp, data_type='task')
    
    def get_task(self, task_id):
        resp = self.gmp.get_task(task_id=task_id)
        return self._get(resp=resp, data_type='task')
    
    def create_task(self, name, target_id, config_id=None, scanner_id=None, comment=None, schedule_id = None):
        """Create a task"""
        # if scanner_id is None:
        #     # try to use default scanner
        #     try:
        #         scanners = self.list_scanners(name=DEFAULT_SCANNER_NAME)
        #         scanner_id = scanners[0]["@id"]
        #     except (ElementNotFound, IndexError, KeyError):
        #         scanner_id = None
        #         pass
        # if config_id is None:
        #     try:
        #         configs = self.list_configs(name=DEFAULT_CONFIG_NAME)
        #         config_id = configs[0]["@id"]
        #     except (ElementNotFound, IndexError, KeyError):
        #         config_id = None
        #         pass
        resp = self.create_task(name=name, config_id=config_id, target_id=target_id, scanner_id=scanner_id, comment=comment, schedule_id=schedule_id)
        return self._create(resp=resp)
    
    def start_task(self, task_id):
        """Start a task."""
        resp = self.gmp.start_task(task_id=task_id)
        return self._command(resp=resp)
    
    def stop_task(self, task_id):
        """stop a task."""
        resp = self.gmp.stop_task(task_id=task_id)
        return self._command(resp=resp)

    def resume_task(self, task_id):
        """resume a task."""
        resp = self.gmp.resume_task(task_id=task_id)
        return self._command(resp=resp)

    def delete_task(self, task_id):
        """delete a task."""
        resp = self.gmp.delete_task(task_id=task_id)
        return self._command(resp=resp)
    
    def list_reports(self, **kwargs):
        """List task reports."""
        if kwargs is not {}:
            def get_filter_str(k, v):
                return "{}=\"{}\"".format(k, v)
            filter_str = " ".join([get_filter_str(k, v) for k, v in six.iteritems(kwargs) if v])
        resp = self.gmp.get_reports(filter_string=filter_str)
        return self._list(resp=resp, data_type="report")
    
    def get_report(self, report_id, report_format_id=None):
        """get task report."""
        if report_format_id is None:
            try:
                formats = self.list_report_formats(name=DEFAULT_FORMAT_NAME)
                report_format_id = formats[0]['@id']
            except (ElementNotFound, IndexError, KeyError):
                report_format_id = None
                pass
            
        resp = self.gmp.get_report(report_id=report_id, report_format_id=report_format_id)
        response = self._command(resp=resp)
        report = response.xml.find("report")
        
        if report.attrib["content_type"] == "text/xml":
            return report
        
        report = response.xml.find(".//report_format").tail
        try:
            return report.decode("base64")
        except AttributeError:
            return report
    
    def list_schedules(self, **kwargs):
        """List schedules and filter by kwargs."""
        if kwargs is not {}:
            def get_filter_str(k, v):
                return "{}=\"{}\"".format(k, v)
            filter_str = " ".join([get_filter_str(k, v) for k, v in six.iteritems(kwargs) if v])
        resp = self.gmp.get_schedules(filter_string=filter_str)
        return self._list(resp=resp, data_type="schedule")
    
    def get_schedule(self, schedule_id, **kwargs):
        """Get schedule by uuid."""
        resp = self.gmp.get_schedule(schedule_id=schedule_id)
        return self._get(resp=resp, data_type='schedule')

    def create_schedule(self, name, icalendar, timezone, comment=None):
        """
        Create a new schedule based in `iCalendar`_ data.
        Example:
            Requires https://pypi.org/project/icalendar/

            .. code-block:: python
                import pytz
                from datetime import datetime
                from icalendar import Calendar, Event
                cal = Calendar()

                cal.add('prodid', '-//Foo Bar//')
                cal.add('version', '2.0')

                event = Event()
                event.add('dtstamp', datetime.now(tz=pytz.UTC))
                event.add('dtstart', datetime(2020, 1, 1, tzinfo=pytz.utc))

                cal.add_component(event)

                gvm.create_schedule(
                    name="My Schedule",
                    icalendar=cal.to_ical(),
                    timezone='UTC'
                )
        Arguments:
            name: Name of the new schedule
            icalendar: `iCalendar`_ (RFC 5545) based data.
            timezone: Timezone to use for the icalender events e.g
                Europe/Berlin. If the datetime values in the icalendar data are
                missing timezone information this timezone gets applied.
                Otherwise the datetime values from the icalendar data are
                displayed in this timezone
            comment: Comment on schedule.
        """
        resp = self.gmp.create_schedule(name=name, icalendar=icalendar, timezone=timezone, comment=comment)
        return self._create(resp=resp)

    def modify_schedule(self, schedule_id, name=None, icalendar=None, timezone=None, comment=None):
        """Modify schedule."""
        resp = self.gmp.modify_schedule(schedule_id=schedule_id, name=name, icalendar=icalendar, timezone=timezone, comment=comment)
        return self._command(resp=resp)
        
    def delete_schedule(self, schedule_id):
        """Delete a schedule."""
        resp = self.gmp.delete_schedule(schedule_id=schedule_id)
        return self._command(resp=resp)
