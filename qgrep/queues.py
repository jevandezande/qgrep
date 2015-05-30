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
        bar = '\033[95m|\033[0m'
        # Process jobs and get a count
        job_list = []
        running_count = {}
        debug = []
        # Iterate over all the jobs and make a list of queues, which each are a list of jobs
        for queue, jobs in self.queues.items():
            # skip large if requested 
            if queue == 'large' and large == False:
                continue
            jobs_running = 0
            username = getpass.getuser()
            for job in jobs:
                jobs_running += 1 if jobs[job].state == 'r' else 0
                # If on the debug queue, show non-user jobs
                if user and (jobs[job].owner != username or queue == 'debug'):
                    jobs.pop(job)
            running_count[queue] = jobs_running
            if queue == 'debug':
                debug = list(jobs.values())
            else:
                job_list.append(list(jobs.values()))
        
        # Form header (without debug queue)
        q_num = len(self.queues) - int('debug' in self.queues)
        # Subtract off queues that are not being shown
        if 'large' in self.queues and not large:
            q_num -= 1
        # Horizontal line
        line = '\033[95m' + '-'*(29*q_num + 1)+ '\033[0m\n'
        name_form = '{} ({:2d} /{:2d})'
        out = line
        # Print a nice header
        for queue, jobs in self.queues.items():
            # skip debug, or large if requested 
            if queue == 'debug' or (queue == 'large' and large == False):
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
            if i > numlines:
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
        out = out + bar + '\n'

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
        

class Job:
    """
    A simple class that contains important information about a job and prints it nicely
    """
    def __init__(self, job_xml):
        self.id, self.name, self.state, self.owner, self.queue = Job.read_job_xml(job_xml)

    def __str__(self):
        """Print a short description of the job, with color"""
        job_form = '{:>6.0f} {:<5s} {:<12s} {}{:2s}\033[0m'
        colors = defaultdict(lambda: '\033[93m', {'r':'\033[92m', 'qw': '\033[94m'})
        return job_form.format(self.id, self.owner[:5], self.name[:12],
                               colors[self.state], self.state)

    @staticmethod
    def read_job_xml(job_xml):
        """
        Read the xml of qstat and find the necessary variables
        """
        id = int(job_xml.find('JB_job_number').text)
        tasks = job_xml.find('tasks')
        # If there are multiple tasks with the same id, make the id a float
        # with the task number being the decimal
        if tasks != None:
            # If it is a range of jobs, e.g. 17-78:1, just take the first
            task = tasks.text.split('-')[0] # If not a range, this does nothing
            id += int(task) / 10**len(task)
        name = job_xml.find('JB_name').text
        state = job_xml.get('state')
        owner = job_xml.find('JB_owner').text
        state2 = job_xml.find('state').text
        queue = job_xml.find('hard_req_queue').text
        if tasks:
            jobs_left = 1
        if (state == 'running' and state2 != 'r') or \
           (state == 'pending' and state2 != 'qw'):
            print('States do not agree: job {}, states:{} {}'.format(id, state, state2))
        return id, name, state2, owner, queue

