# import modules
import bpy
import matplotlib.pyplot as plt
import urllib
import math
import numpy as np
from timeit import default_timer as timer

# import helper-modules
# convert polar to cartesian koordinates:
# import poltocart as ptc

class TLE:
    def get(value, category, satNr):
        with open('TLE/' + category + '.txt') as data:
            content = data.readlines()

            if value == "name":
                return content[(satNr)*3][0:15]
            elif value == "LineNumber":
                return content[((satNr)*3)+1][0:1]
            elif value == "Classification":
                return content[((satNr)*3)+1][7:8]
            elif value == "LaunchYear":
                return content[((satNr)*3)+1][9:11]
            elif value == "LaunchNumber":
                return content[((satNr)*3)+1][11:14]
            elif value == "LaunchPiece":
                return content[((satNr)*3)+1][14:17]
            elif value == "EpochYear":
                return content[((satNr)*3)+1][18:20]
            elif value == "EpochDayFraction":
                return content[((satNr)*3)+1][20:32]
            elif value == "EpochDay":
                return content[((satNr)*3)+1][20:23]
            elif value == "EpochTime":
                return content[((satNr)*3)+1][24:32]
            elif value == "FirstTimeDerivative":
                return content[((satNr)*3)+1][33:43]
            elif value == "SecondTimeDerivative":
                return content[((satNr)*3)+1][44:52]
            elif value == "BSTARDragTerm":
                return content[((satNr)*3)+1][53:61]
            elif value == "Num0":
                return content[((satNr)*3)+1][62:63]
            elif value == "ElementSetNumber":
                return content[((satNr)*3)+1][64:68]
            elif value == "Checksum1":
                return content[((satNr)*3)+1][68:69]

            elif value == "LineNumber2":
                return content[((satNr)*3)+2][0:1]
            elif value == "Number2":
                return content[((satNr)*3)+2][2:7]
            elif value == "Inclination":
                return content[((satNr)*3)+2][8:16]
            elif value == "RAAN":
                return content[((satNr)*3)+2][17:25]
            elif value == "Eccentricity":
                return content[((satNr)*3)+2][26:33]
            elif value == "ArgumentOfPerigee":
                return content[((satNr)*3)+2][34:42]
            elif value == "MeanAnomaly":
                return content[((satNr)*3)+2][43:51]
            elif value == "MeanMotion":
                return content[((satNr)*3)+2][52:63]
            elif value == "Revloution":
                return content[((satNr)*3)+2][63:68]
            elif value == "Checksum2":
                return content[((satNr)*3)+2][68:69]

    # downlaod specific categeory
    def download(category):
        webx_loc = 'http://celestrak.com/NORAD/elements/' + category + '.txt'
        disk_loc = 'TLE/' + category + '.txt'
        urllib.request.urlretrieve(webx_loc, disk_loc)

    # get number of satellites in specific ategory
    def numOfSat(category):
        with open('TLE/' + category + '.txt') as data:
            content = data.readlines()
            return int(len(content) / 3)

    # print specified category
    def printTLE(category, satNr):
        with open('TLE/' + category + '.txt') as data:
            content = data.readlines()
            print(content[((satNr)*3)+1], end="")
            print(content[((satNr)*3)+2], end="")

run_x_times = 10000
timer_list = list()

start_all = timer()

for value_mult in range(0, run_x_times, 1):

    start = timer()

    # controll values
    category = "dummy"
    globalScale = 1
    satSize = 0.5
    orbitSubDivs = 256
    resolution = 5000      # get position of sat each x frames
    threshold = 0.1

    # if internet connection available:
    # TLE.download(category)

    # define
    sce = bpy.context.scene
    n = TLE.numOfSat(category)
    numOfSat = TLE.numOfSat(category)
    rotate = bpy.ops.transform.rotate

    # static
    earthRadius = 6371
    daylengthsec = 86400

    # create list
    xyz = list( [[], [], []] for _ in range(0, numOfSat) )

    # select all -> delete
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # add earth model (sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(size=1, location=(0, 0, 0))
    bpy.ops.object.subdivision_set(level=4)

    # cycle through every satellite in one category
    for i in range(0, numOfSat):

        # define
        satNr = i
        name = TLE.get("name", category, satNr).rstrip("\n")

        # get inclination and convert
        inc_deg = float(TLE.get("Inclination", category, satNr))
        inc_rad = inc_deg / 180 * math.pi

        # get RAAN and convert
        RAAN_deg = float(TLE.get("RAAN", category, satNr))
        RAAN_rad = RAAN_deg * math.pi / 180

        # get AoP and convert
        AoP_deg = float(TLE.get("ArgumentOfPerigee", category, satNr))
        AoP_rad = AoP_deg * math.pi / 180

        # get Mean Motion
        n0 = float(TLE.get("MeanMotion", category, satNr))

        # define duration (time for one rotation around earth)
        duration = int(daylengthsec / n0)

        # calculate apogee / perigee
        semimajoraxis = ((6.6228 / pow(n0, 2/3)) * earthRadius)
        orbitheight = semimajoraxis - earthRadius

        # calculate Eccentricity and convert ("decimal point assumed")
        e0_a = str(TLE.get("Eccentricity", category, satNr))
        e0 = float("0." + e0_a)

        # define apogee and perigee
        apogee = abs(semimajoraxis * (1 + e0) - earthRadius)
        perigee = abs(semimajoraxis * (1 - e0) - earthRadius)

        # print important values

        # print("")
        #
        # print("{:<10}{:<80}".format("name:", name))
        # print("{:<4}/{:<4}".format(i, numOfSat))
        print((value_mult / run_x_times)*100)

        # TLE.printTLE(category, satNr)

        # print("")

        # define names
        orbitname = name
        satname = name + "sat"

        # add orbit, rename orbit
        bpy.ops.mesh.primitive_circle_add(radius=1, vertices=orbitSubDivs)
        bpy.context.object.name = orbitname

        # add sat, rename sat
        bpy.ops.mesh.primitive_cube_add(radius=satSize)
        bpy.context.object.name = satname

        # define object names
        orbit = bpy.context.scene.objects[name]
        sat = bpy.context.scene.objects[name + "sat"]

        # convert orbit to curve and attach sat
        sat.select = False
        orbit.select = True
        sce.objects.active = orbit
        bpy.ops.object.convert(target='CURVE')

        # set orbit duration
        bpy.data.curves[name].path_duration = duration

        # resize orbit
        orbit.scale[0] = apogee
        orbit.scale[1] = perigee

        # move sat to perigee
        sat.location[1] = perigee

        # make sat follow orbit
        sat.select = True
        sce.objects.active = orbit
        bpy.ops.object.parent_set(type='FOLLOW')

        # set duration for 1 revolution
        bpy.data.curves[orbitname].path_duration = duration

        # rotate orbit
        orbit.select = True

        rotate(value=RAAN_rad, axis=(0, 0, 1))
        rotate(value=inc_rad, axis=(1, 0, 0))
        rotate(value=AoP_rad, axis=(0, 0, 1))

        # Getting the position of a satellite:
        # 1. jump to specific frame
        # 2. clear parent (keep transform)
        # 3. get position value and append it to a list
        # 4. reset parent

        for t in range(0, duration, resolution):
            # jump to frame
            sce.frame_set(t)

            # clear parent
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

            # append sat location to list xyz
            xyz[satNr][0].append(sat.location[0])
            xyz[satNr][1].append(sat.location[1])
            xyz[satNr][2].append(sat.location[2])

            # reset parent
            bpy.ops.object.parent_set(type="FOLLOW")

    # end timer -> print runtime
    end = timer()

    # plot x, y and z values ove every satellite for every moment
    # for i in range(0, numOfSat, 1):
    #     plt.plot(xyz[i][0], '-ro')
    #     plt.plot(xyz[i][1], '-go')
    #     plt.plot(xyz[i][2], '-bo')
    #
    # plt.show()

    # Collision Detect
    # https://hanemile.github.io/docs/master.pdf
    # p. 8 - 11

    # create an array filled with 0
    # array[t, y, x]

    # print("")
    # print("{:<10}{:<10}".format("Total duration (sek.): ", end - start))

    timer_list.append(end - start)

# print all timer values
print(timer_list)

# plot the timer_list and show it
plt.plot(timer_list, '-ro')
plt.show()

end_all = timer()
duration_all = start_all - end_all
print(duration_all)

plt.savefig('x10000_res100.png')
