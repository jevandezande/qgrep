from glob import glob
from natsort import natsorted
import subprocess
import os

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
    jmol = "java -jar {} {} -iLs orbs.jmol -g 492x499"
    subprocess.call(jmol.format(jmol_jar, file_name), shell=True)


def ray_trace(file_name):
    """
    Run povray
    :param file_name: name of the povary file (.pov or .pov.ini)
    """
    subprocess.call("/usr/local/bin/povray {}".format(file_name), shell=True)

def draw_folder(folder, options, files='*.molden'):
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
                ray_trace("{}.{}.pov.ini".format(name, orb))
            os.chdir(start_dir)
