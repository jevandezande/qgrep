import subprocess
from xml.etree import ElementTree
from collections import OrderedDict, defaultdict
from itertools import zip_longest, filterfalse
import getpass
from configparser import ConfigParser
import os.path
import re
from .helper import colors

config_file = os.path.join(os.path.expanduser("~"), '.qgrepconfig')
config = ConfigParser()
config.read(config_file)

BAR = colors.purple + '│' + colors.normal
JOB_ID_LENGTH = 7
NAME_LENGTH = 22
SMALL_QUEUE = 3
if 'queues' in config:
    JOB_ID_LENGTH = max(config['queues'].getint('job_id_length', 7), 4)
    NAME_LENGTH = max(config['queues'].getint('name_length', 22), 8)
    SMALL_QUEUE = max(config['queues'].getint('small_queue', 3), 1)
COLUMN_WIDTH = 11 + JOB_ID_LENGTH + NAME_LENGTH


class Queues:
    def __init__(self, omit=[]):
        self.queues = {}
        self.grid_engine, self.tree = self.qxml()
        self.find_sizes()
        self.parse_tree(omit=omit)

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
    def print(self, numjobs=50, person=None):
        """
        Print the queues in a nice table
        """
        # Form header (without small queues)
        large_num = sum([size > SMALL_QUEUE for size in self.sizes.values()])
        # Horizontal line (uses box drawing characters)
        top_line = '\033[95m' + '┌' + '┬'.join(['─'*(COLUMN_WIDTH - 1)]*large_num) + '┐' + '\033[0m\n'
        mid_line = '\033[95m' + '├' + '┼'.join(['─'*(COLUMN_WIDTH - 1)]*large_num) + '┤' + '\033[0m\n'
        bot_line = '\033[95m' + '└' + '┴'.join(['─'*(COLUMN_WIDTH - 1)]*large_num) + '┘' + '\033[0m\n'

        out = top_line

        name_form = '{} ({:2d}/{:2d}/{:2d})'
        # Print a nice header
        for name, queue in sorted(self.queues.items()):
            # Print small queues near the end
            if queue.size <= SMALL_QUEUE:
                continue
            out += BAR + ('{:^' + str(COLUMN_WIDTH-1) + '}').format(name_form.format(name, queue.used, queue.avail, queue.queued))
        out += BAR + '\n' + mid_line
        header = BAR + 'ID'.center(JOB_ID_LENGTH) + ' USER  ' + 'Job Name'.center(NAME_LENGTH) + ' ST'
        out += header*large_num + BAR + '\n' + mid_line

        if person is True:
            person = getpass.getuser()

        # Remove small queues for later use
        job_list = []
        small_queues = []
        for name, queue in sorted(self.queues.items()):
            if queue.size <= SMALL_QUEUE:
                if queue.size > 0:
                    small_queues.append(queue)
                continue
            job_list.append(queue.person_jobs(person).values())

        blank = BAR + ' '*(COLUMN_WIDTH-1)
        for i, job_row in enumerate(zip_longest(*job_list)):
            if i >= numjobs:
                # Add how many more jobs are running in each queue
                for queue in job_list:
                    if len(queue) > numjobs:
                        out += BAR + ('{:^' + str(COLUMN_WIDTH + 7) + '}').format('\033[1m{: >+5} jobs\033[0m'.format(len(queue) - numjobs))
                    else:
                        out += blank
                out += BAR + '\n'
                break
            for job in job_row:
                out += BAR + str(job) if job else blank
            out += BAR + '\n'
        out += mid_line if small_queues else bot_line

        # Display small queues below other queues
        for i, queue in enumerate(small_queues):
            out += queue.print_inline(large_num, None, person) + '\n'
            out += mid_line if i < len(small_queues) - 1 else bot_line

        # Remove newline character
        out = out[:-1]

        return out

    @staticmethod
    def qxml():
        """
        Produce an xml ElementTree object containing all the queued jobs

        Sample output from SGE:

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

    Sample output from PBS:
<Data>
    <Job>
        <Job_Id>77816.icqc</Job_Id>
        <Job_Name>e7_cas2_ddci3_tighter</Job_Name>
        <Job_Owner>sivalingam@icmaster1</Job_Owner>
        <resources_used>
            <cput>21002:04:52</cput>
            <energy_used>0</energy_used>
            <mem>60978424kb</mem>
            <vmem>73997480kb</vmem>
            <walltime>2630:02:36</walltime>
        </resources_used>
        <job_state>R</job_state>
        <queue>batch</queue>
        <server>control</server>
        <Checkpoint>u</Checkpoint>
        <ctime>1488149683</ctime>
        <Error_Path>zeusln1:/home/sivalingam/s4/e7_cas2_ddci3_tighter.err</Error_Path>
        <exec_host>izeusbn13/8-11+izeusbn12/11-12+izeusbn11/12-13</exec_host>
        <Hold_Types>n</Hold_Types>
        <Join_Path>oe</Join_Path>
        <Keep_Files>n</Keep_Files>
        <Mail_Points>a</Mail_Points>
        <mtime>1488149684</mtime>
        <Output_Path>zeus1:/home/sivalingam/s4/e7_cas2_ddci3_tighter.o77816</Output_Path>
        <Priority>0</Priority>
        <qtime>1488149683</qtime>
        <Rerunable>False</Rerunable>
        <Resource_List>
            <nodect>8</nodect>
            <nodes>8</nodes>
            <walltime>8760:00:00</walltime>
        </Resource_List>
        <session_id>3716</session_id>
        <Shell_Path_List>/bin/zsh</Shell_Path_List>
        <euser>sivalingam</euser>
        <egroup>gl-ag orca</egroup>
        <queue_type>E</queue_type>
        <etime>1488149683</etime>
        <submit_args>-j oe -e /home/sivalingam/s4/e7_cas2_ddci3_tighter.err -N e7_cas2_ddci3_tighter -r n e7_cas2_ddci3_tighter.job</submit_args>
        <start_time>1488149684</start_time>
        <Walltime>
            <Remaining>22067782</Remaining>
        </Walltime>
        <start_count>1</start_count>
        <fault_tolerant>False</fault_tolerant>
        <job_radix>0</job_radix>
        <submit_host>zeus1</submit_host>
    </Job>
    ...
</Data>
        """
        cmds = [('sge', 'qstat -u "*" -r -f -xml'), ('pbs', 'qstat -x')]
        for grid_engine, cmd in cmds:
            try:
                xml = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
                return grid_engine, ElementTree.fromstring(xml)
            except FileNotFoundError as e:
                raise Exception("Could not find qstat")
            except subprocess.CalledProcessError as e:
                pass

        raise Exception('Could not generate XML, only PBS and SGE currently supported.')

    def parse_tree(self, omit=[]):
        """
        Parse the xml tree from qxml
        """
        if self.grid_engine == 'sge':
            self.queues = OrderedDict()
            for child in self.tree:
                # Running jobs are arranged by node/queue
                if child.tag == 'queue_info':
                    for node in child:
                        #<Queue-List>
                        #   <name>gen3.q@v10.cl.ccqc.uga.edu</name>
                        name = node.find('name').text.split('@')[0]
                        # If we don't want to display the queue
                        if name in omit:
                            continue
                        if name not in self.queues:
                            self.queues[name] = Queue(self.sizes[name], name)

                        for job_xml in node.iterfind('job_list'):
                            job = Job(job_xml, self.grid_engine)
                            self.queues[name].running[job.id] = job

                # Queued jobs
                elif child.tag == 'job_info':
                    for job_xml in child:
                        job = Job(job_xml, self.grid_engine)
                        name = job.queue.split('@')[0]
                        if name in omit:
                            continue

                        if name not in self.queues:
                            self.queues[name] = Queue(self.sizes[name], name)

                        self.queues[name].queueing[job.id] = job
        elif self.grid_engine == 'pbs':
            self.queues = OrderedDict()
            for job_xml in self.tree:
                job = Job(job_xml, self.grid_engine)
                if job.state == 'c':
                    continue
                queue = job.queue
                if queue not in self.queues:
                    self.queues[queue] = Queue(self.sizes[queue], queue)
                if job.state == 'r':
                    self.queues[queue].running[job.id] = job
                else:
                    self.queues[queue].queueing[job.id] = job
        else:
            raise Exception('Could not read XML, only PBS and SGE currently supported.')


    def find_sizes(self):
        """
        Find the sizes of the queues

        """
        self.sizes = {}
        if self.grid_engine == 'sge':
            """Sample output from 'qstat -g c':
            CLUSTER QUEUE                   CQLOAD   USED    RES  AVAIL  TOTAL aoACDS  cdsuE
            --------------------------------------------------------------------------------
            all.q                             -NA-      0      0      0      0      0      0
            gen3.q                            0.00      0      0      0     16      0     16
            gen4.q                            0.26     31      0     13     48      0      4
            gen5.q                            0.50      4      0      0      4      0      0
            gen6.q                            0.39     19      0      0     19      0      1
            """
            qstat_queues_cmd = "qstat -g c"
            out = subprocess.check_output(qstat_queues_cmd, shell=True)
            for line in out.splitlines()[2:]:
                line = line.decode('UTF-8')
                if 'all.q' == line[:5]:
                    continue
                queue, cqload, used, res, avail, total, aoacds, cdsue = line.split()
                self.sizes[queue] = int(used) + int(avail)
        elif self.grid_engine == 'pbs':
            """sample output from pbsnodes:
izeussn153
    state = job-exclusive
    power_state = Running
    np = 16
    properties = small
    ntype = cluster
    jobs = 0-15/86886.icqc
    status = rectime=1498123346,macaddr=40:f2:e9:c6:22:60,cpuclock=Fixed,varattr=,jobs=86886.icqc(cput=65375153,energy_used=0,mem=118685472kb,vmem=133127908kb,walltime=4154720,session_id=3357),state=free,netload=75804699166624,gres=,loadave=16.00,ncpus=16,physmem=131338172kb,availmem=176492292kb,totmem=265555896kb,idletime=10974874,nusers=1,nsessions=1,sessions=3357,uname=Linux zeussn153 3.10.0-229.el7.x86_64 #1 SMP Fri Mar 6 11:36:42 UTC 2015 x86_64,opsys=linux
    mom_service_port = 15002
    mom_manager_port = 15003
"""
            out = subprocess.check_output('pbsnodes', shell=True).decode('utf-8').strip()
            for job in out.split('\n\n'):
                queue = re.search('properties = (.*)', job).group(1)
                if queue in self.sizes:
                    self.sizes[queue] += 1
                else:
                    self.sizes[queue] = 1
        else:
            raise Exception('Could not read queue sizes, only PBS and SGE currently supported.')


class Queue:
    """
    A class that contains Jobs that are running and queued
    """
    def __init__(self, size, name='', running=None, queueing=None):
        """
        Initialize a queue with its jobs

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

    def print_inline(self, width, max_num=None, person=False):
        """Print jobs inline"""
        if person:
            jobs = self.person_jobs(person)
        else:
            jobs = self.jobs

        used_avail_queued = '{} ({:2d}/{:2d}/{:2d})'.format(self.name, self.used, self.avail, self.queued)
        out = BAR + ('{:^' + str(COLUMN_WIDTH-1) + '}').format(used_avail_queued) + BAR
        for i, job in enumerate(jobs.values()):
            if not (max_num is None) and i >= max_num:
                break
            if not (i + 1) % width:
                out += '\n' + BAR
            out += str(job) + BAR

        # Add blank spots to fill out to end
        if (len(jobs) + 1) % width:
            out += (' '*COLUMN_WIDTH*(width - (len(jobs) + 1) % width))[:-1] + BAR
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
    def __init__(self, job_xml, grid_engine):
        self.id, self.name, self.state, self.owner, self.queue, self.workdir = Job.read_job_xml(job_xml, grid_engine)
        #self.id, self.name, self.state, self.owner, self.queue, self.workdir, (self.nodect, self.nodes) = Job.read_job_xml(job_xml, grid_engine)

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
        job_form = '{:>' + str(JOB_ID_LENGTH) + 'd} {:<5s} {:<' + str(NAME_LENGTH) + 's} {}{:2s}' + colors.normal

        # Color queue status by type, use red if unrecognized
        job_colors = defaultdict(lambda: colors.red, {'r': colors.green, 'qw': colors.blue})

        # Bold the person's jobs
        if self.owner == getpass.getuser():
            owner = colors.bold + '{:5.5s}'.format(self.owner) + colors.normal
        else:
            owner = '{:5.5s}'.format(self.owner)

        return job_form.format(int(self.id), owner, self.name[:NAME_LENGTH],
                            job_colors[self.state], self.state[:2])# + str(self.nodes) + ', ' + str(self.nodect)

    @staticmethod
    def read_job_xml(job_xml, grid_engine):
        """
        Read the xml of qstat and find the necessary variables
        """
        if grid_engine == 'sge':
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
            state = job_xml.get('state').lower()
            owner = job_xml.find('JB_owner').text
            state2 = job_xml.find('state').text
            try:
                queue = job_xml.find('hard_req_queue').text
            except AttributeError as e:
                queue = 'debug.q'
            if (state == 'running' and state2 != 'r') or \
            (state == 'pending' and state2 != 'qw'):
                pass
            return jid, name, state2, owner, queue
        elif grid_engine == 'pbs':
            jid = int(job_xml.find('Job_Id').text.split('.')[0])
            # TODO: deal with job_arrays
            name = job_xml.find('Job_Name').text
            state = job_xml.find('job_state').text.lower()
            owner = job_xml.find('Job_Owner').text.split('@')[0]
            queue = job_xml.find('queue').text
            # Hack misnamed queue
            if queue == 'batch':
                queue = 'big'

            resource_list = job_xml.find('Resource_List')
            nodect, nodes = resource_list.find('nodect').text, resource_list.find('nodes').text

            workdir = None
            try:
                variables = job_xml.find('Variable_List').text.split(',')
                variables = dict(kv.split('=') for kv in variables)
                workdir = variables['PBS_O_WORKDIR']
            except AttributeError:
                pass

            return jid, name, state, owner, queue, workdir
            #return jid, name, state, owner, queue, workdir, (nodect, nodes)
        else:
            raise Exception('Could not read XML, only PBS and SGE currently supported.')
