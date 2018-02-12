import os
import subprocess

from glob import glob

from natsort import natsorted

# Up to but not inclusive
orbs_script_form = """background white

{other}
{rotate}

mo fill nomesh
mo resolution {resolution}

for (var i={start}; i<{end}; ++i)
    mo @{{i}}
    mo translucent 0.3
    write {pic_format} @{{"orbs/{name}." + i + ".{ext}"}}
end for
"""


def make_orbs(file_name, options):
    """
    Make the orbital files
    :file_name: name of the molden file
    :options: rendering options dictionary

    Note: if using POVRay this only produces the pov files,
          ray_trace must be run separately
    """
    name = file_name.split('.')[0]
    script = orbs_script_form.format(name=name, **options)
    open("orbs.jmol", "w").write(script)

    # Run
    jmol_jar = '/home/jevandezande/bin/Jmol/build/Jmol.jar'
    # -g controls window size, jmol adds 8x1 to the window (no idea why)
    jmol = f"java -jar {jmol_jar} {file_name} -iLs orbs.jmol -g 492x499"
    subprocess.call(jmol, shell=True)


def ray_trace(file_name):
    """
    Run povray
    :param file_name: name of the povary file (.pov or .pov.ini)
    """
    subprocess.call(f"/usr/local/bin/povray {file_name}", shell=True)


def draw_folder(options, folder, files='*.molden'):
    """
    Draw all of the files in a folder

    :param folder: the desired folder
    :param options: the desired options
    :param files: glob format selecting all the files to be drawn
    """

    extensions = {
        'povray': 'pov',
        'png': 'png'
    }
    options['ext'] = extensions[options['pic_format']]

    start_dir = os.getcwd()
    draw_dir = 'orbs'
    os.makedirs(draw_dir, exist_ok=True)

    os.chdir(folder)

    # Draw every molden file
    for file_name in natsorted(glob(files)):
        print(file_name)

        # the base name of a file comes before the first dot
        name = file_name.split('.')[0]

        make_orbs(file_name, options)

        # POVRAY rendering
        if options['pic_format'] == 'povray':
            os.chdir(draw_dir)
            for orb in range(options['start'], options['end']):
                print("Ray-tracing orbital: {}\n\n".format(orb))
                make_ini('{}.{}'.format(name, orb), options)
                ray_trace("{}.{}.pov.ini".format(name, orb))
            os.chdir(start_dir)


def make_ini(name, options):
    ini = '''Input_File_Name={0}.pov
Output_to_File=true
Output_File_Type=N
Output_File_Name={0}.png
Width=2032
Height=2004
Antialias=true
Antialias_Threshold=0.01
Antialias_Depth=4
Display=true
Pause_When_Done=true
Quality=11
Sampling_Method=1
Warning_Level=5
Verbose=false
'''
    open(name + '.pov.ini', 'w').write(ini.format(name))


mol_script_form = """background white
write {pic_format} @{{"orbs/{name}." + i + ".{ext}"}}
"""


def draw_mol(file_name, options):
    """
    Make the molecule files
    :file_name: name of the molden file
    :options: rendering options dictionary

    Note: if using POVRay this only produces the pov files,
          ray_trace must be run separately
    """
    name = file_name.split('.')[0]
    script = mol_script_form.format(name=name, **options)
    open("orbs.jmol", "w").write(script)

    # Run
    jmol_jar = '/home/jevandezande/bin/Jmol/build/Jmol.jar'
    # -g controls window size, jmol adds 8x1 to the window (no idea why)
    jmol = "java -jar {} {} -iLs orbs.jmol -g 492x499"
    subprocess.call(jmol.format(jmol_jar, file_name), shell=True)
