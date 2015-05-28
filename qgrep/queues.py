#!/usr/bin/env python3

import subprocess
import xml.etree.ElementTree as ET
from collections import OrderedDict, defaultdict
from itertools import zip_longest
import getpass
from pprint import pprint

class Queues:
    def __init__(self):
        self.tree = self.qxml()
        self.parse_tree()
        self.sizes = {'debug':1, 'gen3':16, 'gen4': 48, 'gen5':2, 'large':1}
    
    def __str__(self):
        """
        Make the tree into a printable form
        """
        return self.print()

    def print(self, numlines=50, large=False, user=False):
        """
        Print the queues in a nice table
        """
        # Process jobs and get a count
        job_list = []
        running_count = []
        debug = []
        debug_jobs_running = 0
        # Iterate over all the jobs and make a list of queues, which each are a list of jobs
        for queue, jobs in self.queues.items():
            # skip large if requested 
            if queue == 'large' and large == False:
                continue
            # set aside debug for later
            if queue == 'debug':
                for job in jobs:
                    debug_jobs_running += 1 if jobs[job].state == 'r' else 0
                    # ignore user command for debug
                    #if user and jobs[job].owner != username:
                    debug.append(jobs[job])
                continue
            jobs_running = 0
            username = getpass.getuser()
            for job in jobs:
                jobs_running += 1 if jobs[job].state == 'r' else 0
                if user and jobs[job].owner != username:
                    jobs.pop(job)
            running_count.append(jobs_running)
            job_list.append(list(jobs.values()))
        
        # Form header
        q_num = len(self.queues)
        # Subtract off queues that are not being shown
        if 'large' in self.queues and not large:
            q_num -= 1
        if 'debug' in self.queues:
            q_num -= 1
        line = '\033[95m' + '-'*(30*q_num + 1)+ '\033[0m\n'
        header_list = list(self.queues.keys())
        name_form = '{} ({:2d} /{:2d})'
        out = line
        out +=  '\033[95m|\033[0m'
        running_iter = iter(running_count)
        # Print a nice header
        for queue, jobs in self.queues.items():
            # skip debug, or large if requested 
            if queue == 'debug' or (queue == 'large' and large == False):
                continue
            count = len(jobs)
            used = next(running_iter)
            avail = self.sizes[queue] - used
            out += '{:^28} \033[95m|\033[0m'.format(name_form.format(queue, used, avail))
        out += '\n' + line
        out +=  '\033[95m|\033[0m'
        header = ' ID  USER    Job Name    St. \033[95m|\033[0m'
        out += header*q_num + '\n'
        out += line
        
        # Iterate through the jobs, job row is a tuple of jobs
        # job is None if they are all used up
        blank = ' '*29 + '\033[95m|\033[0m'
        for i, job_row in enumerate(zip_longest(*job_list)):
            if i > numlines:
                break
            out += '\033[95m|\033[0m'
            for job in job_row:
                if job is None:
                    out += blank
                else:
                    state = job.state
                    out += str(job) + ' \033[95m|\033[0m'
            out += '\n'
        out += line

        # Print the debug queue at the bottom
        num_debug_print = 2
        debug_used = debug_jobs_running
        debug_avail = self.sizes['debug'] - debug_used
        used_avail = 'debug ({} / {})'.format(debug_used, debug_avail)
        out += '\033[95m|\033[0m {:^27s} \033[95m|\033[0m'.format(used_avail)
        out += ' \033[95m|\033[0m '.join(map(str, debug[:num_debug_print]))
        # Add spaces if only a few queued
        if num_debug_print > len(debug):
            out += ' '*29*(num_debug_print - len(debug))
        out += ' \033[95m|\033[0m\n'

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
            return ET.fromstring(xml)
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
                    queue = next(node.iterfind('name')).text.split('.')[0]
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
        

class Job:
    """
    A simple class that conatins important information about a job and prints it nicely
    """
    def __init__(self, job_xml):
        self.id, self.name, self.state, self.owner, self.queue = Job.read_job_xml(job_xml)

    def __str__(self):
        """Print a short description of the job, with color"""
        job_form = '{:>6d} {:<5s} {:<12s} {}{:2s}\033[0m'
        colors = defaultdict(lambda: '\033[93m', {'r':'\033[92m', 'qw': '\033[94m'})
        return job_form.format(self.id, self.owner[:5], self.name[:12],
                               colors[self.state], self.state)

    @staticmethod
    def read_job_xml(job_xml):
        """
        Read the xml of qstat and find the necessary variables
        """
        id = int(next(job_xml.iterfind('JB_job_number')).text)
        name = next(job_xml.iterfind('JB_name')).text
        state = job_xml.get('state')
        owner = next(job_xml.iterfind('JB_owner')).text
        state2 = next(job_xml.iterfind('state')).text
        queue = next(job_xml.iterfind('hard_req_queue')).text
        if (state == 'running' and state2 != 'r') or \
           (state == 'pending' and state2 != 'qw'):
            print('States do not agree: job {}, states:{} {}'.format(id, state, state2))
        return id, name, state2, owner, queue

