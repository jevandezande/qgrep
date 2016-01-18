#!/usr/bin/env python3

import subprocess
from xml.etree import ElementTree
from collections import OrderedDict, defaultdict
from itertools import zip_longest, filterfalse
import getpass
#import logging
from qgrep.helper import colors

SIZES = {'debug': 1, 'gen3': 12, 'gen4': 45, 'gen5': 4, 'large': 1}
BAR = colors.purple + '|' + colors.normal
#logging.basicConfig(filename='.qgrep.log',level=logging.CRITICAL)

class Queues:
    def __init__(self):
        self.queues = {}
        self.tree = self.qxml()
        self.parse_tree()
    
    def __str__(self):
        """
        Make the tree into a printable form
        """
        return self.print()

    def __eq__(self, other):
        """
        Check if queues are equivalent
        """
        if len(self.queues) != len(other.queues):
            return False
        for my_queue, other_queue in zip(self.queues.values(), other.queues.values()):
            if my_queue != other_queue:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    # noinspection PyPep8
    def print(self, numjobs=50, user=None):
        """
        Print the queues in a nice table
        """
        # Form header (without debug and large queue)
        q_num = len(self.queues) - int('debug' in self.queues) - int('large' in self.queues)
        # Horizontal line
        line = '\033[95m' + '-'*(29*q_num + 1)+ '\033[0m\n'

        out = line

        name_form = '{} ({:2d}/{:2d})'
        # Print a nice header
        for name in sorted(self.queues.keys()):
            queue = self.queues[name]
            # skip debug and large
            if name == 'debug' or name == 'large':
                continue
            out +=  BAR + '{:^28}'.format(name_form.format(name, queue.used, queue.avail))
        out += BAR + '\n' + line
        header = BAR + '  ID   USER    Job Name   St'
        out += header*q_num + BAR + '\n' + line
        
        if user is True:
            user = getpass.getuser()
        
        # Remove debug and large
        job_list = []
        for name, queue in sorted(self.queues.items()):
            if name in ['debug', 'large']:
                continue
            job_list.append(queue.person_jobs(user).values())

        blank = BAR + ' '*28
        for i, job_row in enumerate(zip_longest(*job_list)):
            if i >= numjobs:
                # Add how many more jobs are running in each queue
                for queue in job_list:
                    if len(queue) > numjobs:
                        out += BAR + '         \033[1m{: >+3} jobs\033[0m           '.format(len(queue) - numjobs)
                    else:
                        out += blank
                out += BAR + '\n'
                break
            for job in job_row:
                if job is None:
                    out += blank
                else:
                    out += BAR + str(job) 
            out += BAR + '\n'
        out += line

        out += self.queues['large'].print_inline(q_num - 1) + '\n'
        out += line
        out += self.queues['debug'].print_inline(q_num - 1) + '\n'
        # Remove newline
        out += line[:-1]

        return out
        
    @staticmethod
    def qxml():
        """
        Produce an xml ElementTree object containing all the queued jobs

        Sample output
        
    <?xml version='1.0'?>
    <job_info  xmlns:xsd="http://gridengine.sunsource.net/source/browse/*checkout*/gridengine/source/dist/util/resources/schemas/qstat/qstat.xsd?revision=1.11">
    <queue_info>
        <Queue-List>
            <name>debug.q@v3.cl.ccqc.uga.edu</name>
            ...
        </Queue-List>
        <Queue-List>
            <name>gen3.q@v10.cl.ccqc.uga.edu</name>
            ...
            <job_list state="running">
                <JB_job_number>113254</JB_job_number>
                <JB_name>optg</JB_name>
                <JB_owner>mullinax</JB_owner>
                <state>r</state>
                <JAT_start_time>2015-05-11T15:52:49</JAT_start_time>
                <hard_req_queue>large.q<hard_req_queue>
                ...
            </job_list>
        </Queue-List>
        ...
    </queue_info>
    <job_info>
        <job_list state="pending">
            <JB_job_number>112742</JB_job_number>
            <JB_name>CH3ONO2</JB_name>
            <JB_owner>meghaanand</JB_owner>
            <state>qw</state>
            <JB_submission_time>2015-05-08T16:30:25</JB_submission_time>
            <hard_req_queue>large.q<hard_req_queue>
            ...
        </job_list>
    </job_info>
    ...
    </job_info>
        """
        qstat_xml_cmd = "qstat -u '*' -r -f -xml"
        try:
            xml = subprocess.check_output(qstat_xml_cmd, shell=True)
            return ElementTree.fromstring(xml)
        except FileNotFoundError as e:
            raise Exception("Could not find qstat")

    def parse_tree(self):
        """
        Parse the xml tree from qxml
        """
        self.queues = OrderedDict()
        for child in self.tree:
            # Running jobs are arranged by node/queue
            if child.tag == 'queue_info':
                for node in child:
                    #<Queue-List>
                    #   <name>gen3.q@v10.cl.ccqc.uga.edu</name>
                    name = node.find('name').text.split('.')[0]
                    if not name in self.queues:
                        self.queues[name] = Queue(SIZES[name], name)

                    for job_xml in node.iterfind('job_list'):
                        job = Job(job_xml)
                        self.queues[name].running[job.id] = job

            # Queued jobs
            elif child.tag == 'job_info':
                for job_xml in child:
                    job = Job(job_xml)
                    name = job.queue.split('.')[0]
                    if not name in self.queues:
                        self.queues[name] = Queue(SIZES[name], name)

                    self.queues[name].queueing[job.id] = job


class Queue:
    """
    A class that contains Jobs that are running and queued
    """
    def __init__(self, size, name='', running=None, queueing=None):
        """
        Initialize a queue with it's jobs
        
        :param running: an OrderedDict of Jobs that are running
        :param queueing: an OrderedDict of Jobs that are queueing
        """
        self.size = size
        self.name = name
        if running is None:
            self.running = OrderedDict()
        else:
            self.running = running
        if queueing is None:
            self.queueing = OrderedDict()
        else:
            self.queueing = queueing
    
    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for s, o in zip(self.jobs.values(), other.jobs.values()):
            if s != o:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def __len__(self):
        return len(self.running) + len(self.queueing)

    def __list__(self):
        """Make a list of all the Jobs in the queue"""
        return list(self.running.values()) + list(self.queueing.values())

    def __str__(self):
        """Make a string with each job on a new line"""
        return self.print()

    def print(self, numlines=50, person=False):
        if person:
            jobs = self.person_jobs(person)
        else:
            jobs = self.jobs

        out = '\n'.join(list(map(str, jobs.values()))[:numlines])
        if numlines < len(self):
            out += '\n+{} jobs'.format(len(self) - numlines)

        return out

    def print_inline(self, max_num):
        """Print jobs inline"""
        used_avail = '{} ({:2d}/{:2d})'.format(self.name, self.used, self.avail)
        out = BAR + '{:^28s}'.format(used_avail) + BAR
        for job in list(self.jobs.values())[:max_num]:
            out += str(job) + BAR
        # Add spaces if only a few queued
        if len(self.jobs) < max_num:
            out += (' '*29*(max_num - len(self.jobs)))[:-1] + BAR
        return out

    def set(self, job_id, job, position):
        """
        Set a job in the specified position (running or queueing)
        """
        if position == 'running':
            self.running[job_id] = job
        elif position == 'queueing':
            self.queueing[job_id] = job
        else:
            raise Exception("Invalid position, must be either running or"
                            "queueing.")
    
    @property
    def used(self):
        return len(self.running)

    @property
    def avail(self):
        return self.size - self.used

    @property
    def queued(self):
        return len(self.queueing)

    @property
    def jobs(self):
        """
        Makes an OrderedDict of all the running and queueing Jobs
        """
        ret = OrderedDict()
        # OrderedDicts cannot be readily combined
        for k, v in sorted(self.running.items()):
            ret[k] = v
        for k, v in sorted(self.queueing.items()):
            ret[k] = v
        return ret

    def person_jobs(self, person):
        """Return an OrderedDict of Jobs with the specified owner"""
        if not person:
            return self.jobs

        ret = OrderedDict()
        for job in self.jobs.values():
            if job.owner == person:
                ret[job.id] = job
        return ret
        

class Job:
    """
    A simple class that contains important information about a job and prints it
    nicely
    """
    def __init__(self, job_xml):
        self.id, self.name, self.state, self.owner, self.queue = Job.read_job_xml(job_xml)

    def __eq__(self, other):
        if self.id == other.id and \
            self.name == other.name and \
            self.state == other.state and \
            self.owner == other.owner and \
            self.queue == other.queue:
            return True
        return False
    
    def __ne__(self, other):
        return not self == other

    def __str__(self):
        """Print a short description of the job, with color"""
        job_form = '{:>6d} {:<5s} {:<12s} {}{:2s}' + colors.normal

        # Color queue status by type, use red if unrecognized
        job_colors = defaultdict(lambda: colors.red, {'r': colors.green, 'qw': colors.blue})
        
        # Bold the user's jobs
        if self.owner == getpass.getuser():
            owner = colors.bold + self.owner[:5] + colors.normal
        else:
            owner = self.owner[:5]

        return job_form.format(int(self.id), owner, self.name[:12],
                               job_colors[self.state], self.state[:2])

    @staticmethod
    def read_job_xml(job_xml):
        """
        Read the xml of qstat and find the necessary variables
        """
        jid = int(job_xml.find('JB_job_number').text)
        tasks = job_xml.find('tasks')
        # If there are multiple tasks with the same id, make the id a float
        # with the task number being the decimal
        if tasks is not None:
            # If it is a range of jobs, e.g. 17-78:1, just take the first
            task = tasks.text.split('-')[0]  # If not a range, this does nothing
            # SGE is being cute and comma separates two numbers if sequential
            task = task.split(',')[0]
            jid += int(task) / 10 ** len(task)
        name = job_xml.find('JB_name').text
        state = job_xml.get('state')
        owner = job_xml.find('JB_owner').text
        state2 = job_xml.find('state').text
        try:
            queue = job_xml.find('hard_req_queue').text
        except AttributeError as e:
            queue = 'debug.q'
        if (state == 'running' and state2 != 'r') or \
           (state == 'pending' and state2 != 'qw'):
            #logging.warning('States do not agree: job {}, states:{}, {}'.format(jid, state, state2))
            pass
        return jid, name, state2, owner, queue
