import re
import sys

import numpy as n

class Segments(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.ip = [p1, p2]
        self.flags = False

    def addip(self, pointlist):
        ipt = [i for i in pointlist if i not in self.ip]
        self.ip.extend(ipt)

    def reset(self):
        self.ip = [self.p1, self.p2]
        self.flags = False

    def flag(self):
        self.flags = True

def intersectionpoint(p1, q1, p2, q2):
    r = q1 - p1
    s = q2 - p2
    if n.cross(r, s) == 0:
        if n.cross((p1 - p2), s) == 0:  # colinear case
            tzero = n.dot((p2 - p1), r) / float(n.dot(r, r))
            tone = n.dot((q2 - p1), r) / float(n.dot(r, r))
            uzero = n.dot((p1 - p2), s) / float(n.dot(s, s))
            uone = n.dot((q1 - p2), s) / float(n.dot(s, s))
            if 1 >= tzero >= 0 and 1 >= tone >= 0: return [tuple(p2), tuple(q2)]
            if 1 >= uzero >= 0 and 1 >= uone >= 0: return [tuple(p1), tuple(q1)]
            if 1 >= tzero >= 0 and 1 >= uone >= 0: return [tuple(p2), tuple(q1)]
            if 1 >= tone >= 0 and 1 >= uzero >= 0: return [tuple(p1), tuple(q2)]
        elif n.cross((p1 - p2), s) != 0:  # Parallel Line Case
            return None
    elif n.cross(r, s) != 0:
        t = n.cross((p2 - p1), s) / float(n.cross(r, s))
        u = n.cross((p2 - p1), r) / float(n.cross(r, s))
        if 1 >= t >= 0 and 1 >= u >= 0:
            p = p1 + t * r
            return [tuple(p)]
        else:
            return None


def GenerateGraph(street):
    sc = list(street.values())
    listofvertex = []
    listofedges = []
    for i in range(len(sc) - 1):
        for j in range(i + 1, len(sc)):
            for k in sc[i]:
                for l in sc[j]:
                    intersect = intersectionpoint(n.array(k.p1), n.array(k.p2), n.array(l.p1), n.array(l.p2))
                    if intersect is not None:
                        k.addip(intersect)
                        l.addip(intersect)
                        k.flag()
                        l.flag()
    for i in sc:
        for k in i:
            k.ip.sort()
            for l in k.ip:
                if l not in listofvertex and k.flags: listofvertex.append(l)
            for l in range(len(k.ip)-1):
                if k.flags and (listofvertex.index(k.ip[l]),listofvertex.index(k.ip[l+1])) not in listofedges:
                    listofedges.append(
                    (listofvertex.index(k.ip[l]), listofvertex.index(k.ip[l+1])))
    return [list((i, listofvertex[i])) for i in range(len(listofvertex))], listofedges


def main():
    ### YOUR MAIN CODE GOES HERE

    ### sample code to read from stdin.

    ### make sure to remove all spurious print statements as required

    ### by the assignment
    street = {}
    while True:

        line = sys.stdin.readline()
        if line == '':
            break
        graphtest = re.match(r'[^\S]*[g][^\S]*$', str(line))
        removetest = re.match(r'[^\S]*[r]\s[^\S]*"(.*[A-Za-z\s])"[^\S]*$', str(line))
        cmdtest = re.match(r'[^\S]*[ac]\s[^\S]*"(.*[A-Za-z\s])"\s[^\S]*', str(line))
        tupletest = re.sub(r'\(([^\S]*.-?\d*?[^\S]*,.[^\S]*-?\d*?[^\S]*)\)|\s|\(([^\S]*-?.\d*?[^\S]*,.[^\S]*-?\d*?['
                           r'^\S]*)\)', '', str(line))
        if cmdtest is not None and tupletest == re.sub(r'\s', '', cmdtest.group()):
            streetname = str.lower(re.search(r'(?<=\")(.*)(?=\")', str(line)).group())
            if (str(line).strip())[0] == 'a':
                if streetname in street:
                    sys.stderr.write(
                        "Error: Street already in the graph; if you need to change the street, please use 'c' command\n")
                    sys.stderr.flush()
                else:
                    pointlist = eval('[(' + '),('.join(re.findall(r'\((.*?,.*?)\)', str(line))) + ')]')
                    segmentlist = []
                    for i in range(len(pointlist) - 1):
                        segmentlist.append(Segments(pointlist[i], pointlist[i + 1]))
                    street[str(streetname)] = segmentlist
            elif (str(line).strip())[0] == 'c':
                if streetname in street:
                    pointlist = eval('[(' + '),('.join(re.findall(r'\((.*?,.*?)\)', str(line))) + ')]')
                    segmentlist = []
                    for i in range(len(pointlist) - 1):
                        segmentlist.append(Segments(pointlist[i], pointlist[i + 1]))
                    street[str(streetname)] = segmentlist
                    for i in street.keys():
                        for streetsegs in street[i]:
                            streetsegs.reset()
                else:
                    sys.stderr.write("Error: Street not found; if you need to add a street please use 'a' command\n")
                    sys.stderr.flush()
        elif removetest is not None:
            streetname = str.lower(re.search(r'(?<=\")(.*)(?=\")', str(line)).group())
            try:
                del street[streetname]
                for i in street.keys():
                    for streetsegs in street[i]:
                        streetsegs.reset()
            except KeyError:
                sys.stderr.write("Error: Street not found; if you need to add a street please use 'a' command\n")
                sys.stderr.flush()
        elif graphtest is not None:
            (V, E) = GenerateGraph(street)
            sys.stdout.write("Vertex = {\n")
            for i in V: sys.stdout.write("%1d:  (%.2f,%.2f)\n" % (i[0], i[1][0], i[1][1]))
            sys.stdout.write("}\n")
            sys.stdout.write("Edges = {\n")
            for i in E: sys.stdout.write("<%1d,%1d>,\n" % (i[0], i[1]))
            sys.stdout.write("}\n")
        else:
            sys.stderr.write(
                "Error: formatting of the command or coordinates do not match what is expected: e.g a ""Weber Street"" (2,1) "
                "(3,3)\n")
            sys.stderr.flush()
        #print('read a line:', line)

    #print('Finished reading input')

    # return exit code 0 on successful termination

    sys.exit(0)


if __name__ == '__main__':
    main()
