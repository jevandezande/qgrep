#!/usr/bin/env python3

import subprocess
from xml.etree import ElementTree
from collections import OrderedDict, defaultdict
from itertools import zip_longest
import getpass


class Queues:
    def __init__(self):
        self.queues = OrderedDict()
        self.tree = self.qxml()
        self.parse_tree()
        self.sizes = {'debug': 1, 'gen3': 16, 'gen4': 48, 'gen5': 2, 'large': 1}
    
    def __str__(self):
        """
        Make the tree into a printable form
        """
        return self.print()

    # noinspection PyPep8
    def print(self, numjobs=50, user=False):
        """
        Print the queues in a nice table
        """
        bar = '\033[95m|\033[0m'
        # Process jobs and get a count
        job_list = []
        running_count = {}
        debug = []
        large = []
        # Iterate over all the jobs and make a list of queues, which each are a list of jobs
        for queue, jobs in self.queues.items():
            jobs_running = 0
            username = getpass.getuser()
            for job in jobs:
                jobs_running += 1 if jobs[job].state == 'r' else 0
                # If on the debug queue, show non-user jobs
                if (user and jobs[job].owner != username) and queue != 'debug' and queue != 'large':
                    jobs.pop(job)
            running_count[queue] = jobs_running
            if queue == 'debug':
                debug = list(jobs.values())
            elif queue == 'large':
                large = list(jobs.values())
            else:
                job_list.append(list(jobs.values()))
        
        # Form header (without debug and large queue)
        q_num = len(self.queues) - int('debug' in self.queues) - int('large' in self.queues)
        # Horizontal line
        line = '\033[95m' + '-'*(29*q_num + 1)+ '\033[0m\n'
        name_form = '{} ({:2d} /{:2d})'
        out = line
        # Print a nice header
        for queue, jobs in self.queues.items():
            # skip debug and large
            if queue == 'debug' or queue == 'large':
                continue
            used = running_count[queue]
            avail = self.sizes[queue] - used
            out +=  bar + '{:^28}'.format(name_form.format(queue, used, avail))
        out += bar + '\n' + line
        header = bar + '  ID   USER    Job Name   St'
        out += header*q_num + bar + '\n' + line
        
        # Iterate through the jobs, job row is a tuple of jobs
        # job is None if they are all used up
        blank = bar + ' '*28
        for i, job_row in enumerate(zip_longest(*job_list)):
            if i >= numjobs:
                break
            for job in job_row:
                if job is None:
                    out += blank
                else:
                    out += bar + str(job) 
            out += bar + '\n'
        out += line

        # Print the debug queue at the bottom
        num_debug_print = q_num - 1
        debug_used = running_count['debug']
        debug_avail = self.sizes['debug'] - debug_used
        used_avail = 'debug ({} / {})'.format(debug_used, debug_avail)
        out += bar + '{:^28s}'.format(used_avail) + bar
        for job in debug[:num_debug_print]:
            out += str(job) + bar
        # Add spaces if only a few queued
        if num_debug_print > len(debug):
            out += (' '*29*(num_debug_print - len(debug)))[:-1]
        out += bar + '\n' + line

        # Print the large queue at the bottom
        num_large_print = q_num - 1
        large_used = running_count['large']
        large_avail = self.sizes['large'] - large_used
        used_avail = 'large ({} / {})'.format(large_used, large_avail)
        out += bar + '{:^28s}'.format(used_avail) + bar
        for job in large[:num_large_print]:
            out += str(job) + bar
        # Add spaces if only a few queued
        if num_large_print > len(large):
            out += (' '*29*(num_large_print - len(large)))[:-1]
        out += bar + '\n'

        # Remove newline
        out += line[:-1]

        print(out)
        
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
            print("Could not find qstat")
            raise e

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
                    queue = node.find('name').text.split('.')[0]
                    if not queue in self.queues:
                        self.queues[queue] = OrderedDict()

                    for job_xml in node.iterfind('job_list'):
                        job = Job(job_xml)
                        self.queues[queue][job.id] = job

            # Queued jobs
            elif child.tag == 'job_info':
                for job_xml in child:
                    job = Job(job_xml)
                    queue = job.queue.split('.')[0]
                    if not queue in self.queues:
                        self.queues[queue] = OrderedDict()

                    self.queues[queue][job.id] = job


class Queue:
    """
    A simple class that contains Jobs that are running and queued
    """
    def __init__(self, size, running, queueing):
        """
        Initialize a queue with it's jobs
        
        :param running: an OrderedDict of Jobs that are running
        :param queueing: and OrderedDict of Jobs that are queueing
        """
        self.size = size
        self.running = running
        # not queued to prevent clash
        self.queueing = queueing

    def __len__(self):
        return self.size

    def __list__(self):
        """Make a list of all the Jobs in the queue"""
        return list(self.running.values()) + list(self.queueing.values())

    # May not work right, may need to have the first argument be Queue as that
    # is what self is
    #@accepts(Queue, (int, float))
    def __getitem__(self, job_id):
        if job_id in self.running:
            return self.running[job_id]
        elif job_id in self.queueing:
            return self.queueing[job_id]
        raise KeyError("Cannot find the Job with id: " + str(job_id))

    #@accepts((int, float), Job, str)
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

    def person_jobs(self, owner):
        """Return a list of the Jobs with the specified owner"""
        raise NotImplementedError()
        

class Job:
    """
    A simple class that contains important information about a job and prints it
    nicely
    """
    def __init__(self, job_xml):
        self.id, self.name, self.state, self.owner, self.queue = Job.read_job_xml(job_xml)

    def __str__(self):
        """Print a short description of the job, with color"""
        job_form = '{:>6.0f} {:<5s} {:<12s} {}{:2s}\033[0m'
        colors = defaultdict(lambda: '\033[93m', {'r': '\033[92m',
                                                  'qw': '\033[94m'})
        return job_form.format(self.id, self.owner[:5], self.name[:12],
                               colors[self.state], self.state)

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
            jid += int(task) / 10 ** len(task)
        name = job_xml.find('JB_name').text
        state = job_xml.get('state')
        owner = job_xml.find('JB_owner').text
        state2 = job_xml.find('state').text
        queue = job_xml.find('hard_req_queue').text
        if (state == 'running' and state2 != 'r') or \
           (state == 'pending' and state2 != 'qw'):
            print('States do not agree: job {}, states:{} {}'.format(jid, state, state2))
        return jid, name, state2, owner, queue

