#!/usr/bin/env python3

import subprocess
import xml.etree.ElementTree as ET
from collections import OrderedDict
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
        # Iterate over all the jobs and make a list of queues, which each are a list of jobs
        for queue, jobs in self.queues.items():
            # skip large if requested
            if 'large' in self.queues and queue == 'large' and large == False:
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
        if 'large' in self.queues and not large:
            q_num -= 1
        line = '\033[95m' + '-'*30*q_num + '\033[0m\n'
        header_list = list(self.queues.keys())
        name_form = '{} ({:2d} /{:2d})'
        out = line
        running_iter = iter(running_count)
        # Print a nice header
        for queue, jobs in self.queues.items():
            # skip the large queue if requested
            if 'large' in self.queues and queue == 'large' and large == False:
                continue
            count = len(jobs)
            used = next(running_iter)
            avail = self.sizes[queue] - used
            out += '{:^28} \033[95m|\033[0m'.format(name_form.format(queue, used, avail))
        out += '\n' + line
        header = ' ID  USER    Job Name    St. \033[95m|\033[0m'
        out += header*q_num + '\n'
        out += line
        
        # Iterate through the jobs, job row is a tuple of jobs
        # job is None if they are all used up
        blank = ' '*29 + '\033[95m|\033[0m'
        for i, job_row in enumerate(zip_longest(*job_list)):
            if i > numlines:
                break
            for job in job_row:
                if job is None:
                    out += blank
                else:
                    state = job.state
                    out += str(job) + ' \033[95m|\033[0m'
            out += '\n'
        out += line

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
                    for job in node.iterfind('job_list'):
                        state = job.get('state')
                        id = next(job.iterfind('JB_job_number')).text
                        name = next(job.iterfind('JB_name')).text
                        owner = next(job.iterfind('JB_owner')).text
                        state2 = next(job.iterfind('state')).text
                        req_queue = next(job.iterfind('hard_req_queue')).text
                        if not (state == 'running' and state2 == 'r'):
                            raise Exception('States do not agree')
                        
                        self.queues[queue][id] = Job(int(id), name, owner, state2)
            # Queued jobs
            elif child.tag == 'job_info':
                for job in child:
                    state = job.get('state')
                    id = next(job.iterfind('JB_job_number')).text
                    name = next(job.iterfind('JB_name')).text
                    owner = next(job.iterfind('JB_owner')).text
                    state2 = next(job.iterfind('state')).text
                    queue = next(job.iterfind('hard_req_queue')).text.split('.')[0]
                    if not queue in self.queues:
                        self.queues[queue] = OrderedDict()
                    if not (state == 'pending' and state2 == 'qw'):
                        raise Exception('States do not agree: job {}, states:' +
                                        '{} {}'.format(id, state, state2))

                    self.queues[queue][id] = Job(int(id), name, owner, state2)


class Job:
    """
    A simple class that conatins important information about a job and prints it nicely
    """
    def __init__(self, id, name, owner, state):
        self.id = id
        self.name = name
        self.owner = owner
        self.state = state

    def __str__(self):
        job_form = '{:>6d} {:<5s} {:<12s} {}{:2s}\033[0m'
        color = '\033[93m'
        if self.state == 'r':
            color = '\033[92m'
        elif self.state == 'qw':
            color = '\033[94m'
        return job_form.format(self.id, self.owner[:5], self.name[:12],
                               color, self.state)

