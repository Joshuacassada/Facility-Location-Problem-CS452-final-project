Facility Location (2D)

The input describes a facility-location instance in a 2-dimensional plane.

The first line contains:

f — number of facilities

c — number of customers

The remainder of the input has four parts:

A line of f facility opening costs

f lines of facility coordinates (x y)

A line of c customer demands

c lines of customer coordinates (x y)

Distances between facilities and customers are computed using Euclidean distance.

🔢 Input Format
f c
<facility opening costs>
<facility_1_x> <facility_1_y>
...
<facility_f_x> <facility_f_y>
<customer demands>
<customer_1_x> <customer_1_y>
...
<customer_c_x> <customer_c_y>

📤 Output Format

Your output must contain:

Total cost of the solution

List of opened facilities and the customers assigned to them

facility_index: customer_1 customer_2 ...


Only facilities that are opened should appear.

🧪 Example Input
3 5
12 10 15
2 3
8 1
5 7
3 5 4 6 2
1 1
3 4
6 2
4 6
9 3

🧪 Example Output
34.82
0: 1 3
2: 0 2 4

📐 Facility Location (Distance Matrix Form)

Instead of coordinates, the input may provide direct shipping costs from every customer to every facility.

The first line contains:

f — number of facilities

c — number of customers

This is followed by c lines, each containing f floating-point distances.

🔢 Input Format
f c
<distances for customer 0 to all facilities>
<distances for customer 1 to all facilities>
...
<distances for customer c-1 to all facilities>

🧪 Example Input

(matches your uploaded distance matrix)

3 5
2.24 7.00 7.21
1.41 5.83 3.61
4.12 2.24 5.10
3.61 6.40 1.41
7.00 2.24 5.66

🧪 Example Output
33.28
0: 0 1
2: 2 3 4
