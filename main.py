import shapefile
import collections
import argparse
import os
import time

def hello_user():
    global lines_shp, points_shp, accuracy, step

    shp_files = []
    for file in os.listdir():
        if file.endswith("shp"):
            shp_files.append(file[:-4])

    os.system('cls')
    print("GREAT GIS_EQUALIZER 2000")
    
    print("\nAll shapefiles in current catalog:")
    for num in range(len(shp_files)):
        print(num + 1, shp_files[num])
    lines_shp = shp_files[int(input("Lines shapefile:")) - 1]
    print("\nLines set to", lines_shp)
    if lines_shp == "":
        exit()

    print("\nAll shapefiles in current catalog:")
    for num in range(len(shp_files)):
        print(num + 1, shp_files[num])
    points_shp = shp_files[int(input("Elevation shapefile:")) - 1]
    print("\nElevations set to", lines_shp)
    if points_shp == "":
        exit()

    accuracy = input("\nChoose accuracy (5):")
    if accuracy:
        accuracy = float(accuracy)
    if accuracy == "":
        accuracy = 5

    step = input("\nChoose step (10):")
    if step:
        step = int(step)
    if step == "":
        step = 10

    print("\nLet's go...\n")


class Road():

    def __init__(self, corners):
        self.corners = corners
        self.points = []
        self.num_of_elevations = 5
        self.divide_sectors()
        self.dict_from_points()

    def divide_sectors(self):
        """
        Perform operation on sectors to get smooth transition from point to point.
        """
        sectors = self.roads_sectors()
        for sector in sectors:
            self.points += (self.div_sector(sector))

    def dict_from_points(self):
        """
        Transforms list to dictionary for further use.
        """
        lis = collections.OrderedDict()
        for pair in self.points:
            lis[pair] = 0
        self.points = lis

    def roads_sectors(self):
        """
        Creates list of pairs of keys points of line. 
        Pair contains start and end of each sector.
        """
        sectors = []
        for step in range(len(self.corners) - 1):
            sectors.append((self.corners[step], self.corners[step + 1]))
        return sectors

    def div_sector(self, sector):
        """
        Divide sector and returns list of points 1 meter between each. 
        """
        x1, y1 = sector[0]
        x2, y2 = sector[1]
        diag = ((max(x1, x2) - min(x1, x2))**2 + (max(y1, y2) - min(y1, y2))**2)**0.5
        x_coeff = ((max(x1, x2) - min(x1, x2)) / diag)
        y_coeff = ((max(y1, y2) - min(y1, y2)) / diag)
        divided_sector = []
        if x1 <= x2:
            if y1 <= y2:
                for i in range(int(diag)):
                    divided_sector.append((x1 + x_coeff * i, y1 + y_coeff * i))
            if y1 > y2:
                for i in range(int(diag)):
                    divided_sector.append((x1 + x_coeff * i, y1 - y_coeff * i))
        if x1 >= x2:
            if y1 <= y2:
                for i in range(int(diag)):
                    divided_sector.append((x1 - x_coeff * i, y1 + y_coeff * i))
            if y1 > y2:
                for i in range(int(diag)):
                    divided_sector.append((x1 - x_coeff * i, y1 - y_coeff * i))

        return divided_sector

    def grand_finale(self):
        """
        Fills empty points' values.
        """
        list_of_sectors = []  # list of sectors with empty points
        list_of_known = []  # list of known values

        t = []
        for key, value in self.points.items():

            t.append(key)
            if value != 0:
                list_of_sectors.append(t)
                t = []
                list_of_known.append(value)
        list_of_sectors.append(t)

        # Number of elev points which's been binded to road
        self.num_of_elevations = len(list_of_known)

        if len(list_of_known) < 2:
            print(f"Not enough point on line with {list_of_sectors[0][0]}")
            return

        # Central sectors
        for sec_num in range(len(list_of_sectors) - 2):
            cur_sec = list_of_sectors[sec_num + 1]

            val_1 = list_of_known[sec_num]
            val_2 = list_of_known[sec_num + 1]
            len_s = len(cur_sec)
            p_val = ((val_1 - val_2) / len_s)

            for points in range(len(cur_sec)):
                self.points[cur_sec[points]] = round(
                    (val_1 - (p_val * (points + 1))), 2)

        # First sector
        first_sector = list_of_sectors[0]
        for points in range(len(first_sector)):

            val_1 = list_of_known[0] - ((list_of_known[1] - list_of_known[0]) /
                                        len(list_of_sectors[1])) * len(first_sector)
            val_2 = list_of_known[0]
            len_s = len(first_sector)
            p_val = (val_1 - val_2) / len_s

            self.points[first_sector[points]] = round(
                (val_1 - (p_val * (points + 1))), 2)

        # Last sector
        last_sector = list_of_sectors[-1]
        for points in range(len(last_sector)):

            val_1 = list_of_known[-1]
            val_2 = list_of_known[-1] - ((list_of_known[-2] - list_of_known[-1]) /
                                         len(list_of_sectors[-2])) * len(last_sector)
            len_s = len(last_sector)
            p_val = (val_1 - val_2) / len_s

            self.points[last_sector[points]] = round(
                (val_1 - (p_val * (points + 1))), 2)

    def make_steps(self):

        temp = collections.OrderedDict()
        for key, value in list(self.points.items())[::step]:
            temp[key] = value

        self.points = temp


class Elevation():

    def __init__(self, coordinates_and_elev):
        self.points = coordinates_and_elev
        self.dict_from_points()

    def dict_from_points(self):
        lis = {}
        for pair in self.points:
            lis[pair[0]] = pair[1]
        self.points = lis

    def get_number(self):
        return len(self.points)


def parse():
    global lines_shp, points_shp, accuracy, step

    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--lines',
                        help='reads the name of shapefile with lines',
                        default='lines')
    parser.add_argument('-p', '--points',
                        help='reads the name of shapefile with elevations',
                        default='point')
    parser.add_argument('-a', '--accuracy',
                        help='specify the accuracy of connection', default=0.5, type=float)
    parser.add_argument('-s', '--step',
                        help='specify distance between points', default=5, type=int)
    args = parser.parse_args()

    lines_shp = args.lines
    points_shp = args.points
    accuracy = args.accuracy
    step = args.step


def read_files():
    global road_list
    global elevations

    road_list = []
    elevations = None

    with open(f'{lines_shp}.shp', 'rb') as myshp:
        with open(f'{lines_shp}.dbf', 'rb') as mydbf:
            r = shapefile.Reader(shp=myshp, dbf=mydbf)
            roads = r.shapes()
            for num_road in range(len(roads)):
                road_list.append(Road(roads[num_road].points))

    with open(f'{points_shp}.shp', 'rb') as myshp:
        with open(f'{points_shp}.dbf', 'rb') as mydbf:
            r = shapefile.Reader(shp=myshp, dbf=mydbf)
            shapes = r.shapeRecords()
            elev_points = []
            for shape in range(len(shapes)):
                elev_points.append(
                    (tuple(shapes[shape].shape.points[0]), shapes[shape].record[0]))
            elevations = Elevation(elev_points)

            # Little assertion to validate points layer
            n_of_zeros = list(elevations.points.values()).count(0)
            assert ((len(elevations.points) / 2) > n_of_zeros), "Too many Zeroes in points layer"


def elev_from_points_to_roads():
    """
    Bondes known elevation points to empty points 
    created along lines with given accuracy.
    """
    global road_list, elevations, acc_level
    elevation_points = elevations.points
    acc_level = 0

    for road in road_list:

        print("\nProcessing road with coordinates", list(road.points.items())[0][0])
        for elev_k, elev_v in elevation_points.items():
            target_point = [0, accuracy]
            for road_k, road_v in road.points.items():
                x1, y1 = elev_k
                x2, y2 = road_k
                diag = ((max(x1, x2) - min(x1, x2))**2 +
                        (max(y1, y2) - min(y1, y2))**2)**0.5

                # Finding The least diagonal possible for elevation                
                if (diag < target_point[1]): 
                    target_point = [road_k, diag] 
            if target_point[1] < accuracy:
                print("Coordinates ", target_point[0], " bonded to elev = ", elev_v, "with accuracy", round(target_point[1], 2))
                acc_level += 1 
                road.points[target_point[0]] = elev_v

        print("Road finished")


def main():

    # parse()
    hello_user()
    read_files()
    elev_from_points_to_roads()
    for road in road_list:
        road.grand_finale()
        road.make_steps()


def save_results():
    """
    Saving results in 'results' shapefile trio. 
    """
    test_shp = shapefile.Writer('result')
    test_shp.field('elev', 'F', decimal=2)

    test_shp.shapeType = 1

    for road in road_list:
        for coord, elev in road.points.items():
            x, y = coord
            test_shp.point(x, y)
            test_shp.record(elev)

    test_shp.save("result")


def show_statistic():
    # os.system('cls')
    print()
    for number_of_road in range(len(road_list)):
        print(f'Line №{number_of_road+1} contains', (len(road_list[number_of_road].corners)-1), 'sector(s)')
        print(f'After transormation it contains', len(road_list[number_of_road].points), 'points')
        print(road_list[number_of_road].num_of_elevations, 'elevations were connected')
        print()

    print('-----------------------------')
    print('Totally there are', elevations.get_number(), 'elevations')
    print(acc_level, 'of them were connected to lines')
    print('With accuracy =', accuracy, 'metres')
    print()

if __name__ == "__main__":
	start_time = time.time()

	main()
	save_results()
	show_statistic()

	print("Finished in", round((time.time() - start_time), 2), "second(s).")
