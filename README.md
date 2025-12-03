Input

The program requires three main types of input: clients, facilities, and a coverage distance.

1. Clients (people needing service)

Each client has:

A name

Coordinates (x, y)

Example:

Clients:
- Alice: (2, 3)
- Bob: (5, 4)
- Charlie: (1, 7)
- Diana: (6, 8)

2. Facilities (possible locations we may choose to open)

Each facility has:

A name

Coordinates (x, y)

An initial “open or not” flag (usually False at the start)

Example:

Facilities:
- Facility1: (2, 4), open = False
- Facility2: (5, 5), open = False
- Facility3: (1, 6), open = False

3. Coverage Distance

Maximum distance allowed between a facility and a client for that facility to serve the client.

Example:

Coverage distance: 2.5



Output

The solver returns the optimal set of facilities and relevant information.

1. Chosen Facilities

Which facilities the algorithm decides to open.

Example:

Open facilities: Facility1, Facility2

2. Coverage Mapping

Shows which clients are assigned to which facility.

Example:

Coverage:
- Facility1 covers: Alice, Charlie
- Facility2 covers: Bob, Diana