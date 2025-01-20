from __future__ import print_function, division
import sys
import argparse
import numpy as np

class P3DfmtFile(object):
    """P3Dfmt file representation."""

    def __init__(self, filename=None):
        if filename:
            self.load(filename=filename)
        else:
            self.__nblocks = 0
            self.__coords = None

    @property
    def nblocks(self):
        """Number of blocks in the file."""
        return self.__nblocks

    @property
    def coords(self):
        """Return coordinates stored in the file."""
        return self.__coords

    def load(self, filename):
        """Load mesh blocks from the given file."""
        with open(filename, 'r') as fp:
            try:
                # Read the number of blocks
                first_line = fp.readline().strip()
                if not first_line:
                    raise ValueError("File is empty or missing block count line.")

                self.__nblocks = int(first_line)
                if self.__nblocks != 1:
                    raise ValueError(f"Expected exactly 1 block, but found {self.__nblocks} blocks.")

                # Read the dimensions of the block
                second_line = fp.readline().strip()
                if not second_line:
                    raise ValueError("Missing dimensions line.")

                idim, jdim = map(int, second_line.split())

                # Initialize storage for coordinates
                x = np.zeros((idim, jdim), 'f8')
                y = np.zeros((idim, jdim), 'f8')

                # Read x-coordinates
                for j in range(jdim):
                    x_values = []
                    while len(x_values) < idim:
                        line = fp.readline().strip()
                        if not line:
                            raise ValueError(f"Unexpected end of file while reading x-coordinates for row {j+1}.")
                        x_line = list(map(float, line.split()))
                        x_values.extend(x_line)
                    if len(x_values) > idim:
                        print(f"Warning: Row {j+1} - Excess x-coordinates detected and truncated.")
                    x[:, j] = x_values[:idim]

                # Read y-coordinates
                for j in range(jdim):
                    y_values = []
                    while len(y_values) < idim:
                        line = fp.readline().strip()
                        if not line:
                            print(f"Error: Unexpected end of file while reading y-coordinates for row {j+1}.")
                            print(f"Suggestion: Check the input file for missing data in row {j+1}.")
                            sys.exit(1)
                        y_line = list(map(float, line.split()))
                        y_values.extend(y_line)
                    if len(y_values) > idim:
                        print(f"Warning: Row {j+1} - Excess y-coordinates detected and truncated.")
                    y[:, j] = y_values[:idim]

                self.__coords = [(x, y)]

            except ValueError as e:
                print(f"Error while reading file: {e}")
                sys.exit(1)

class GmshFile(object):
    """Gmsh file representation."""

    def __init__(self):
        self.__nodes = []
        self.__elements = []

    @property
    def nodes(self):
        return self.__nodes

    @property
    def elements(self):
        return self.__elements

    def save(self, filename=None):
        """Save file to stdout if no filename is given."""
        if filename:
            fp = open(filename, 'w')
        else:
            fp = sys.stdout

        self._write_header(fp)
        self._write_nodes(fp)
        self._write_elements(fp)

    def _write_header(self, out):
        out.write('$MeshFormat\n')
        out.write('2.2 0 8\n')
        out.write('$EndMeshFormat\n')

    def _write_nodes(self, out):
        out.write('$Nodes\n')
        out.write(f'{len(self.__nodes)}\n')
        for node in self.__nodes:
            out.write(f'{node[0]} {node[1]} {node[2]} {node[3]}\n')
        out.write('$EndNodes\n')

    def _write_elements(self, out):
        out.write('$Elements\n')
        out.write(f'{len(self.__elements)}\n')
        for el in self.__elements:
            out.write(' '.join(map(str, el)) + '\n')
        out.write('$EndElements\n')

    def consume(self, p3dfmt_file):
        for blkn, (x, y) in enumerate(p3dfmt_file.coords):
            idim, jdim = x.shape

            # Filling nodes list
            for i in range(idim):
                for j in range(jdim):
                    node_id = len(self.__nodes) + 1
                    self.__nodes.append((node_id, x[i, j], y[i, j], 0.0))  # z is set to 0.0 for 2D

            # Generating 2D elements (quadrilaterals)
            for i in range(idim - 1):
                for j in range(jdim - 1):
                    el_id = len(self.__elements) + 1
                    n1 = i * jdim + j + 1
                    n2 = (i + 1) * jdim + j + 1
                    n3 = (i + 1) * jdim + (j + 1) + 1
                    n4 = i * jdim + (j + 1) + 1

                    self.__elements.append([el_id, 3, 2, 1, n1, n2, n3, n4])  # Quadrilateral element

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert P3Dfmt mesh files to GMSH format.')
    parser.add_argument('input', help='Input P3Dfmt file path.')
    parser.add_argument('output', help='Output GMSH file path.')

    args = parser.parse_args()

    p3d_file = P3DfmtFile(args.input)
    gmsh_file = GmshFile()

    gmsh_file.consume(p3d_file)
    gmsh_file.save(args.output)
